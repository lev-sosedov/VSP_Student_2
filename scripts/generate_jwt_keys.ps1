param(
    [string]$PrivateKeyPath = "../VSP_Student_2_jwt_private_key.pem",
    [string]$PublicKeyPath = "../VSP_Student_2_jwt_public_key.pem"
)

$private = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot $PrivateKeyPath))
$public = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot $PublicKeyPath))

if ((Test-Path -LiteralPath $private) -or (Test-Path -LiteralPath $public)) {
    throw "Refusing to overwrite an existing JWT key file."
}

& openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out $private
if ($LASTEXITCODE -ne 0) { throw "Private-key generation failed." }
& openssl pkey -in $private -pubout -out $public
if ($LASTEXITCODE -ne 0) { throw "Public-key generation failed." }

Write-Host "JWT keys generated outside the repository. Keep the private key restricted."
