export const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export const exportToCSV = (data: unknown[], filename: string) => {
  const headers = Object.keys(data[0] as Record<string, unknown>)
  const rows = data.map((item: unknown) =>
    headers.map((header) => {
      const value = (item as Record<string, unknown>)[header]
      if (typeof value === 'string' && value.includes(',')) {
        return `"${value}"`
      }
      return value
    })
  )

  const csvContent = [
    headers.join(','),
    ...rows.map((row) => row.join(',')),
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadFile(blob, `${filename}.csv`)
}

export const exportToJSON = (data: unknown, filename: string) => {
  const jsonString = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8;' })
  downloadFile(blob, `${filename}.json`)
}
