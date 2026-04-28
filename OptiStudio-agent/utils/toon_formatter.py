def dict_to_toon(data: list[dict], table_name: str = "Result") -> str:
    """
    Converts a list of dictionaries (e.g., SQL row results) into
    TOON (Token-Oriented Object Notation) to save tokens when passing into LLM contexts.
    
    Example output:
    users[2]{id,name,role}:
      1,Alice,admin
      2,Bob,user
    """
    if not data:
        return f"{table_name}[0]{{}}:\n  (no results)"

    keys = list(data[0].keys())
    count = len(data)
    
    header = f"{table_name}[{count}]{{{','.join(keys)}}}:\n"
    
    rows = []
    for row in data:
        values = []
        for key in keys:
            # Handle nulls and commas in strings
            val = str(row.get(key, ""))
            if "," in val:
                val = f'"{val}"'
            values.append(val)
        rows.append("  " + ",".join(values))
        
    return header + "\n".join(rows)
