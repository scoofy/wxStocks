from collections import namedtuple
import numpy as np



def return_percentile_rank(stock_list, attribute_name_str, stock_symbol=None, reverse=False):
    ''' Return a dictionary of stocks' percentile rank based on an attribute they all share.
        If a particular symbol is entered, only return it's percentile rank.
    '''
    num_of_stocks = len(stock_list)
    sort_list = []
    error_count = 0
    for this_stock in stock_list:
        try:
            value = float(getattr(this_stock, attribute_name_str))
            symbol = this_stock.symbol
            sort_list.append([symbol, value])
        except Exception, exception:
            # There needs to be a case here for stocks that fail... ideally there should be none though
            if error_count < 10:
                print line_number(), exception, "Stock appears to have no %s attribute." % attribute_name_str
            else:
                print line_number(), exception, "Multiple stocks appears to have no %s attribute." % attribute_name_str
                return
            error_count+=1

    if len(sort_list) > 1:
        sort_list.sort(key = lambda x: x[1], reverse=reverse) # False -> highest ranking ends last, i.e. closer to 100%

    if len(stock_list) != len(sort_list):
        print line_number(), "Error: Some Stocks not included in margin rank function, cannot calculate"
        return

    percentile_dict = {}
    count = 1 # Need to use ordinal numbering
    for sorted_tuple in sort_list:
        position = float(count) # prevent 0th position by starting count with 1 -> proper percentile division below
        percentile_rank = (position/num_of_stocks) * 100.
        percentile_dict[sorted_tuple[0]] = percentile_rank # ticker = percentile_rank

        position = None
        count += 1
    if not stock_symbol:
        return percentile_dict
    else:
        return percentile_dict.get(stock_symbol)

FormulaResult = namedtuple("FormulaResult", ['ticker', 'value', 'not_none', 'avg_value', 'standard_deviation'])
def return_aaii_formula_standard_deviation_of_each_stock_in_group(stock_list, formula):
    tuple_list = []
    for stock in stock_list:
        ticker = stock.ticker
        value = formula(stock)
        not_none = value is not None
        avg_value = None
        standard_deviation = None

        stock_tuple = FormulaResult(ticker = ticker,
                                    value = value,
                                    not_none = not_none,
                                    avg_value = avg_value,
                                    standard_deviation = standard_deviation
                                    )
        tuple_list.append(stock_tuple)
    not_none_value_list = []
    for stock_tuple in tuple_list:
        if stock_tuple.not_none:
            not_none_value_list.append(stock_tuple.value)
    avg_value = np.mean(not_none_value_list)
    standard_deviation = np.std(not_none_value_list)
    print line_number(), "\n" * 5
    print 'avg_value:', avg_value
    print 'standard_deviation', standard_deviation
    print "\n"
    new_tuple_list = []
    for stock_tuple in tuple_list:
        avg_value, standard_deviation
        new_stock_tuple = stock_tuple._replace(avg_value = avg_value)
        new_stock_tuple = new_stock_tuple._replace(standard_deviation = standard_deviation)
        new_tuple_list.append(new_stock_tuple)
    return new_tuple_list



