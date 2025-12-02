terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "92ed9a57-4c58-40e4-971d-19ca85b360fd"
}

# Data sources for existing resources
data "azurerm_resource_group" "rg" {
  name = "chaussup-resource-group"
}

data "azurerm_virtual_network" "vnet" {
  name                = "vnet-francecentral-chaussup"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_subnet" "appgw_subnet" {
  name                 = "snetappgwchaussup"
  virtual_network_name = data.azurerm_virtual_network.vnet.name
  resource_group_name  = data.azurerm_resource_group.rg.name
}

data "azurerm_public_ip" "appgw_ip" {
  name                = "GWChaussup"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_key_vault" "kv" {
  name                = "chaussup-vault"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_key_vault_certificate" "ssl_cert" {
  name         = "chaussup-duck-dns-org-cert"
  key_vault_id = data.azurerm_key_vault.kv.id
}

# Managed Identity for Application Gateway to access Key Vault
resource "azurerm_user_assigned_identity" "appgw_identity" {
  name                = "appgw-identity"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
}

# RBAC role assignment for App Gateway to read secrets from Key Vault
resource "azurerm_role_assignment" "appgw_kv_secrets" {
  scope                = data.azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.appgw_identity.principal_id
}

data "azurerm_client_config" "current" {}

# Application Gateway
resource "azurerm_application_gateway" "appgw" {
  name                = "GWChaussup"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  zones               = ["1", "2", "3"]

  sku {
    name = "WAF_v2"
    tier = "WAF_v2"
  }

  autoscale_configuration {
    min_capacity = 0
    max_capacity = 10
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.appgw_identity.id]
  }

  gateway_ip_configuration {
    name      = "appGatewayIpConfig"
    subnet_id = data.azurerm_subnet.appgw_subnet.id
  }

  frontend_port {
    name = "port_80"
    port = 80
  }

  frontend_port {
    name = "port_443"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "appGwPublicFrontendIpIPv4"
    public_ip_address_id = data.azurerm_public_ip.appgw_ip.id
  }

  backend_address_pool {
    name         = "chaussup-webapp"
    ip_addresses = ["172.16.2.4"]
  }

  backend_http_settings {
    name                  = "GWBack"
    cookie_based_affinity = "Disabled"
    port                  = 5000
    protocol              = "Http"
    request_timeout       = 20
  }

  ssl_certificate {
    name                = "chaussup-duckdns-cert"
    key_vault_secret_id = data.azurerm_key_vault_certificate.ssl_cert.secret_id
  }

  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "appGwPublicFrontendIpIPv4"
    frontend_port_name             = "port_80"
    protocol                       = "Http"
  }

  http_listener {
    name                           = "https-listener"
    frontend_ip_configuration_name = "appGwPublicFrontendIpIPv4"
    frontend_port_name             = "port_443"
    protocol                       = "Https"
    ssl_certificate_name           = "chaussup-duckdns-cert"
  }

  request_routing_rule {
    name                        = "https-to-webapp"
    rule_type                   = "Basic"
    priority                    = 100
    http_listener_name          = "https-listener"
    backend_address_pool_name   = "chaussup-webapp"
    backend_http_settings_name  = "GWBack"
  }

  request_routing_rule {
    name                       = "http-to-https-redirect"
    rule_type                  = "Basic"
    priority                   = 200
    http_listener_name         = "http-listener"
    redirect_configuration_name = "http-to-https-redirect"
  }

  redirect_configuration {
    name                 = "http-to-https-redirect"
    redirect_type        = "Permanent"
    target_listener_name = "https-listener"
    include_path         = true
    include_query_string = true
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
    request_body_check = true
    max_request_body_size_kb = 128
    file_upload_limit_mb = 100
  }

  frontend_port {
    name = "port_8443"
    port = 8443
  }

  # Add backend pool for Wazuh
  backend_address_pool {
    name         = "wazuh-backend"
    ip_addresses = ["172.16.3.4"]
  }

  # Add backend HTTP settings for Wazuh
  backend_http_settings {
    name                  = "wazuh-settings"
    cookie_based_affinity = "Disabled"
    port                  = 443
    protocol              = "Https"
    request_timeout       = 60
    pick_host_name_from_backend_address = false
  }

  # Add HTTPS listener on port 8443
  http_listener {
    name                           = "wazuh-listener"
    frontend_ip_configuration_name = "appGwPublicFrontendIpIPv4"
    frontend_port_name             = "port_8443"
    protocol                       = "Https"
    ssl_certificate_name           = "chaussup-duckdns-cert"
  }

  # Add routing rule for Wazuh
  request_routing_rule {
    name                       = "wazuh-rule"
    rule_type                  = "Basic"
    priority                   = 300
    http_listener_name         = "wazuh-listener"
    backend_address_pool_name  = "wazuh-backend"
    backend_http_settings_name = "wazuh-settings"
  }

  enable_http2 = true

  depends_on = [azurerm_role_assignment.appgw_kv_secrets]
}