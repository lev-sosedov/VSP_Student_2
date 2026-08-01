$ErrorActionPreference = "Stop"

$branchName = "codex/security-config-stage1"
$commitMessage = "secure environment configuration and OpenAPI baselines"

if (-not (Test-Path ".git")) {
    throw "Запустите скрипт из корня репозитория VSP_Student_2"
}

$currentBranch = git branch --show-current
if ($LASTEXITCODE -ne 0) {
    throw "Не удалось определить текущую ветку"
}

if ($currentBranch -eq "master") {
    git switch -c $branchName
    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось создать ветку $branchName"
    }
} elseif ($currentBranch -ne $branchName) {
    throw "Ожидалась ветка master или $branchName, сейчас открыта $currentBranch"
}

# Секретные локальные файлы остаются на компьютере, но удаляются из индекса Git.
git rm --cached --ignore-unmatch -- "services/*/.env"
git rm -r --cached --ignore-unmatch -- .idea

python scripts/check_configuration.py
if ($LASTEXITCODE -ne 0) {
    throw "Проверка конфигурации завершилась ошибкой"
}

git add -A
git diff --cached --check
if ($LASTEXITCODE -ne 0) {
    throw "git diff --check обнаружил ошибки"
}

git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Не удалось создать commit"
}

git push -u origin $branchName
if ($LASTEXITCODE -ne 0) {
    throw "Не удалось отправить ветку в GitHub"
}

$pullRequestBody = @"
## Что изменено

- секретные `.env` удалены из отслеживания Git;
- добавлены безопасные `.env.example` для всех сервисов;
- пароли и JWT-ключ вынесены из Docker Compose;
- разделены development и production Compose-конфигурации;
- зафиксированы публичные и внутренние API;
- сохранены OpenAPI baseline всех девяти сервисов;
- добавлены скрипты проверки конфигурации и OpenAPI.

## Проверки

- `python scripts/check_configuration.py`
- `git diff --check`
- OpenAPI baseline повторно экспортирован и проверен
"@

$bodyPath = Join-Path $env:TEMP "vsp-stage1-pr-body.md"
Set-Content -Path $bodyPath -Value $pullRequestBody -Encoding utf8

gh pr create `
    --draft `
    --base master `
    --head $branchName `
    --title "Secure environment configuration and OpenAPI baselines" `
    --body-file $bodyPath

if ($LASTEXITCODE -ne 0) {
    throw "Ветка отправлена, но Pull Request создать не удалось"
}

Write-Host "Готово: ветка отправлена и draft Pull Request создан." -ForegroundColor Green
