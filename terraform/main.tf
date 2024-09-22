provider "azurerm" {
  features {}
 client_id       = "ae7ceba5-183a-4bad-8ea0-fa67f858a3f7"
  client_secret   = "iuK8Q~ovCfQI_58IJLFDg~WYN3A3sAMiDYOhmadL"
  tenant_id       = "b0487131-816d-4f4c-b2bd-9ff425f91c14"
  subscription_id = "f622a4e7-3ae9-479e-b33c-5eea6719eb24"
}

resource "azurerm_resource_group" "rg" {
  name     = "myResourceGroup"
  location = "East US"
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "myAKSCluster"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "myAKSCluster"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_DS2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
    service_cidr  = "10.0.0.0/16"
    dns_service_ip = "10.0.0.10"
  }

  # Optional: Enable monitoring if needed
  # addon_profile {
  #   oms_agent {
  #     enabled = true
  #   }
  # }
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive = true
}
