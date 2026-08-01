param(
    [string]$PrivateKeyPath = "../../VSP_Student_2_jwt_private_key.pem",
    [string]$PublicKeyPath = "../../VSP_Student_2_jwt_public_key.pem"
)

$repositoryRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$repositoryRootWithSeparator = $repositoryRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$private = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot $PrivateKeyPath))
$public = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot $PublicKeyPath))

if ($private.StartsWith($repositoryRootWithSeparator, [StringComparison]::OrdinalIgnoreCase) -or
    $public.StartsWith($repositoryRootWithSeparator, [StringComparison]::OrdinalIgnoreCase)) {
    throw "JWT key paths must be outside the repository root: $repositoryRoot"
}

if ((Test-Path -LiteralPath $private) -or (Test-Path -LiteralPath $public)) {
    throw "Refusing to overwrite an existing JWT key file."
}

 $openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl -and (Test-Path -LiteralPath "C:\Program Files\Git\usr\bin\openssl.exe")) {
    $openssl = Get-Item -LiteralPath "C:\Program Files\Git\usr\bin\openssl.exe"
}
if (-not $openssl) {
    throw "OpenSSL was not found. Install OpenSSL or Git for Windows before generating JWT keys."
}

& $openssl.Source genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out $private
if ($LASTEXITCODE -ne 0) { throw "Private-key generation failed." }
try {
    & $openssl.Source pkey -in $private -pubout -out $public
    if ($LASTEXITCODE -ne 0) { throw "Public-key generation failed." }
} catch {
    if (Test-Path -LiteralPath $private) { Remove-Item -LiteralPath $private -Force }
    throw
}

Write-Host "JWT keys generated outside the repository. Keep the private key restricted."
