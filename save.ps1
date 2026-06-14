# =============================================
# 메이트 프로젝트 — 자동 저장 스크립트
# 사용법: .\save.ps1 "저장 메시지"
# 예시:  .\save.ps1 "화면 2 온보딩 완성"
# =============================================

# Git 경로 설정 (Portable Git)
$git = "$env:USERPROFILE\PortableGit\bin\git.exe"

# 저장소 경로
$repoPath = "c:\Users\mc950\OneDrive\Desktop\mate"
Set-Location $repoPath

# 커밋 메시지 (입력 없으면 기본값 사용)
$message = if ($args[0]) { $args[0] } else { "업데이트 - $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }

Write-Host ""
Write-Host "💾 메이트 프로젝트 저장 중..." -ForegroundColor Cyan
Write-Host "📝 저장 메시지: $message" -ForegroundColor Yellow
Write-Host ""

# 변경된 파일 모두 추가
& $git add .

# 커밋 (변경사항 있을 때만)
$status = & $git status --porcelain
if ($status) {
    & $git commit -m $message
    Write-Host ""
    Write-Host "📤 GitHub에 업로드 중..." -ForegroundColor Cyan
    & $git push origin main
    Write-Host ""
    Write-Host "✅ 저장 완료! GitHub에서 확인하세요:" -ForegroundColor Green
    Write-Host "   https://github.com/minchul-der/mate-app" -ForegroundColor Blue
} else {
    Write-Host "ℹ️  변경된 파일이 없습니다. 저장할 내용이 없어요!" -ForegroundColor Yellow
}

Write-Host ""
