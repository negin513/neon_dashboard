function table_to_csv(source) {
    const columns = Object.keys(source.data);
    const nrows = source.get_length();
    const lines = [columns.join(',')];

    for (let i = 0; i < nrows; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j];
            let cellValue = source.data[column][i];
            // Check if the column name suggests it's a time/date column
            // Adjust the condition to fit your specific column naming
            if (column.toLowerCase().includes('time') || column.toLowerCase().includes('date')) {
                // Assuming UNIX timestamp in milliseconds, adjust accordingly
                cellValue = new Date(cellValue).toISOString();
            }
            row.push(cellValue.toString());
        }
        lines.push(row.join(','));
    }
    return lines.join('\n').concat('\n');
}


const filename = download_site+'_'+download_var+'_'+download_freq+'_data.csv'
const filetext = table_to_csv(source)
const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename)
} else {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.target = '_blank'
    link.style.visibility = 'hidden'
    link.dispatchEvent(new MouseEvent('click'))
}
