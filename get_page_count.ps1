$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('D:\Python\BuyZone\MH_Club_E_Commerce_Project_Documentation.docx')
    $pages = $doc.ComputeStatistics(2)
    Write-Host "EXACT_PAGE_COUNT: $pages"
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
