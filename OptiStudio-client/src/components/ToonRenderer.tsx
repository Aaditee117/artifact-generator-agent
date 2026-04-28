
export const ToonRenderer = ({ text }: { text: string }) => {
  // Try to find the TOON signature
  // e.g. SQLResult[2]{Name,Role}:
  //  Aaditee Agrawal,Admin
  //  Shobhit Vishwakarma,Architect
  const toonRegex = /([a-zA-Z0-9_]+)\[(\d+)\]\{(.*?)\}:\n([\s\S]*)/;

  const parts = text.split('\n\n');

  return (
    <>
      {parts.map((part, index) => {
        const match = part.match(toonRegex);
        if (match) {
          const [_, tableName, rowCount, colString, rowsString] = match;
          const cols = colString.split(',').map(c => c.trim());
          const rows = rowsString.split('\n').filter(r => r.trim().length > 0).map(r => {
            // Very simple CSV-like split, assumes no commas inside values for now
            return r.trim().split(',').map(cell => cell.trim());
          });

          return (
            <div key={`table-${index}`} style={{ marginTop: '15px', overflowX: 'auto', marginBottom: '15px' }}>
              <div style={{ background: '#e3f2fd', color: '#0d47a1', padding: '8px 12px', borderTopLeftRadius: '6px', borderTopRightRadius: '6px', fontWeight: 'bold', fontSize: '13px', border: '1px solid #bbdefb', borderBottom: 'none' }}>
                {tableName} ({rowCount} rows)
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px', background: 'white', border: '1px solid #e0e0e0' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8f9fa' }}>
                    {cols.map((c, i) => (
                      <th key={`th-${i}`} style={{ padding: '10px 12px', borderBottom: '2px solid #ddd', textAlign: 'left', color: '#495057' }}>{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, ri) => (
                    <tr key={`tr-${ri}`} style={{ borderBottom: '1px solid #eee' }}>
                      {row.map((cell, ci) => (
                        <td key={`td-${ci}`} style={{ padding: '10px 12px', color: '#333' }}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={cols.length} style={{ padding: '15px', textAlign: 'center', color: '#777' }}>No data found.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          );
        }

        // Regular text
        const isSql = part.startsWith('Executing SQL:');
        return (
          <div key={`text-${index}`} style={{ 
            fontFamily: isSql ? 'monospace' : 'inherit', 
            background: isSql ? '#f8f9fa' : 'transparent', 
            padding: isSql ? '12px' : '0', 
            borderRadius: '6px',
            border: isSql ? '1px solid #e9ecef' : 'none',
            color: isSql ? '#d63384' : 'inherit',
            whiteSpace: 'pre-wrap',
            marginBottom: '10px'
          }}>
            {part}
          </div>
        );
      })}
    </>
  );
};
