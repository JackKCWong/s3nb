import polars as pl
from IPython.core.magic import register_line_magic

@register_line_magic
def df(line):
    """
    Custom cell magic to convert the return value of Python code into a Polars DataFrame.

    Usage:
    %%df myvar
    <python code>

    Args:
        line (str): The line following the magic command, typically the variable name.
        cell (str): The content of the cell.

    Returns:
        None: The resulting DataFrame is stored in the user's namespace.
    """
    # Execute the cell code and capture the result
    from IPython import get_ipython
    ip = get_ipython()
    result = ip.run_cell(line)
    
    if result is None:
        raise ValueError("The cell code did not return any value.")

    var_name = line.strip().split('=')[0]
    
    try:
        df = pl.from_dicts(ip.user_ns[var_name])
    except Exception as e:
        raise ValueError(f"Failed to convert the result to a Polars DataFrame: {e}")

    ip.user_ns[var_name] = df

    return df
