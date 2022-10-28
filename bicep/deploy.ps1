param(
    [Parameter()]
    [string]
    $resourceGroupName
)

# Create resource group if not exists
az group create `
  --name $resourceGroupName `
  --location eastus

az deployment group create `
  --name New-Guid `
  --resource-group $resourceGroupName `
  --template-file main.bicep `
  --parameters ./environments/development.parameters.json