import shutil

def __measure_column_widths(lengths, row_count):
    '''
    Given a list of string lengths and a defined number of rows, calculate the individual widths
    that are needed to fill the columns.
    '''
    columns = (len(lengths) + row_count - 1) // row_count
    widths = []
    for i in range(columns):
        column_elems = lengths[i*row_count:(i+1)*row_count]
        column_width = max(column_elems)
        widths.append(column_width)
    return widths

def __measure_total_columns_width(lengths, row_count):
    '''
    Given a list of string lengths and a defined number of rows, calculate the total width
    that is needed to fill the columns. Space around columns is not included in the sum.
    '''
    return sum(__measure_column_widths(lengths, row_count))

def __print_layout(elems, row_count, space_left, space_between):
    '''
    Print the given elems to stdout using a column format. The number of rows is specified.
    The width results from the element widths and row_count
    '''
    column_widths = __measure_column_widths([len(e) for e in elems], row_count)
    rows = []
    for row_i in range(row_count):
        row = space_left * " "
        elem_ids = range(row_i, len(elems), row_count)
        needed_padding = 0
        column_i = 0
        for elem_id in elem_ids:
            elem = elems[elem_id]
            row += (needed_padding * " ") + elem
            needed_padding = space_between + column_widths[column_i] - len(elem)
            column_i += 1
        rows.append(row)
    print("\n".join(rows))

def print_in_columns(elems, space_left=0, space_right=0, space_between=2):
    '''
    Print the given list of strings in an ls-like column format into the terminal.
    The order of elements is first down, then to the right.
    The number of columns is maximized to use the available space.
    '''
    width = shutil.get_terminal_size().columns
    count = len(elems)
    lengths = [len(elem) for elem in elems]

    # start with the absolute minimum possible number of rows
    rows = (sum(lengths) + width - 1) // width
    columns = (count + rows - 1) // rows

    while columns > 1 and __measure_total_columns_width(lengths, rows) + (columns - 1) * space_between + space_left + space_right > width:
        # Layout does not fit, try to increase the row count or decrease the column count
        if rows < columns:
            rows += 1
            columns = (count + rows - 1) // rows
        else:
            columns -= 1
            rows = (count + columns - 1) // columns

    __print_layout(elems, rows, space_left, space_between)
