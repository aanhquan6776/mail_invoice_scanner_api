import re

def get_text(filepath):
    """
        get the text from input file
    """
    text = ""
    with open(filepath, "r", encoding ='utf-8') as inputfile:
        for line in inputfile:
            text = text + line
    return text


def cut_top(text):
    """
        the text before the seller information is not necessary
    """
    begin = 0
    beginregex = "From"
    tmp = 0
    while True:
        # Find the last "From" to get the exact location of seller information
        from_found = re.search(beginregex, text[tmp:])
        if from_found:
            begin = tmp + from_found.start()
            tmp = tmp + from_found.end()
        else:
            break
               
    return text[begin:]


def truncate(text):
    """
        get rid of the unnecessary text
    """
    result = text
    result = cut_top(result)
    return result


def preprocess_date(datestring):
    result = []
    datestring = datestring.replace(",", "")
    result = datestring.split()
    return result


def extract_date(datestring):
    """
        get the day, month, year in the string
    """
    month_dict = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    tokens = preprocess_date(datestring)
    
    year = ''
    month = ''
    day = ''
    
    yearregex = r'(19|20)\d{2}'
    dayregex = r'([12]\d|3[01]|0?[1-9])'
    
    for token in tokens:
        """
            loop over all the integer in the string to check if it is day or month or year
        """
        if (year=='') or (month=='') or (day==''):
            if (month=='') and (token in month_dict):
                month = month_dict[token]
            if (day=='') and re.match(dayregex, token):
                day = token
            if (year=='') and re.match(yearregex, token):
                year = token
            
    if len(day)==1:
        day = '0' + day
    return day + '/' + month + '/' + year


def get_field(text, key_field):
    """
        Get from text the information of the key_field with the other fields to help truncate the result
    """
    FIELDS = {'From':'Seller', 'Subject':'', 'Date':'CreateDate', 'To':''}
    
    # result = ""
    if key_field not in FIELDS.keys():
        return ""
    
    begin = 0
    end = len(text)
    
    found = re.search(key_field, text[begin:end], re.IGNORECASE)
    if found:
        # search for the key_field (begin point of result)
        begin = begin + found.end()
        if text[begin]==':':
            begin += 1
            
        for field in FIELDS.keys():
            # search for the other fields (end point of result)
            endfound = re.search(field, text[begin:end], re.IGNORECASE)
            if endfound:
                # update the endpoint (the closest field to the key_field)
                end = min(end, begin + endfound.start())
    
    return text[begin:end].strip()


def string_to_float(numstring):
    """
        convert a string with splitter ','' and '.' to float
    """
    result = 0
    tmp = 0
    begin = 0
    end = len(numstring)
    
    if not re.match(r"\d{1}", numstring[-3]):
        tmp = tmp + int(numstring[-2])/10 + int(numstring[-1])/100
        end = end - 3
        
    for i in range(begin, end):
        if re.match(r"\d{1}", numstring[i]):
            result = result*10 + int(numstring[i])
            
    return result + tmp


def get_currency(string):
    CURRENCIES = {'[$]':'Dollar', 'VND':'VND', '₫':'VND', 'đ':'VND'}
    for currency in CURRENCIES.keys():
        if re.search(currency, string, re.IGNORECASE):
            return CURRENCIES[currency]
    return ""


def get_cost(text):
    """
        get the total cost in the text
    """
    KEYWORDS = ['total', 'amount paid', 'amount', 'charged', 'total payment', 'tổng', \
                'tổng cộng', 'số tiền', 'so tien', 'tong', 'tong cong']   
    VI_COST_REGEXES = [r'\d{1,3}([.]\d{3})+([,]\d{2})?', r'\d+([,]\d{2})?']
    EN_COST_REGEXES = [r'\d{1,3}([,]\d{3})+([.]\d{2})?', r'\d+([.]\d{2})?']
    
    expense = 0
    currency = ""
    
    begin = 0
    end = len(text)
    
    tmp = 0
    for keyword in KEYWORDS: 
        # search for keyword, which is followed by the total cost
        keyword_found = re.search(keyword, text[begin:], re.IGNORECASE)
        if keyword_found:
            tmp = max(tmp, keyword_found.end())
    
    begin = tmp
    if begin > 0:
        # if the keyword exists
        l = end+1
        r = end
        for vi_cost_regex in VI_COST_REGEXES:
            # search for the cost right after the keyword
            found = re.search(vi_cost_regex, text[begin:], re.IGNORECASE)
            if found:
                if l>found.start() or \
                    (l==found.start() and r-l+1<found.end()-found.start()+1):   
                    l = found.start()
                    r = found.end()
                    
        for en_cost_regex in EN_COST_REGEXES:
            # search for the cost right after the keyword
            found = re.search(en_cost_regex, text[begin:], re.IGNORECASE)
            if found:
                if l>found.start() or \
                    (l==found.start() and r-l+1<found.end()-found.start()+1):
                    l = found.start()
                    r = found.end()
        if l<=end:
            expense = string_to_float(text[begin+l : begin+r])
            currency = get_currency(text[max(begin+l-10, begin): min(begin+r+10, end)])
        else:
            pass
    else:
        pass
    
    return expense, currency 


# def extract_from_email_bodytext(inputfile):
#     """
#         from a text inputfile which contains body text of the email, extract the information
#     """    
#     result = {}
#     text = get_text(inputfile)
#     text = truncate(text)
    
#     result.update({'create_date': extract_date(get_field(text, 'Date'))})
#     result.update({'seller': get_field(text, 'From')})
#     expense_and_currency = get_cost(text)
#     result.update({'total': expense_and_currency[0]})
#     result.update({'currency': expense_and_currency[1]})
    
#     return result


def extract_from_email_bodytext(text):
    """
        from a text inputfile which contains body text of the email, extract the information
    """    
    result = {}
    text = truncate(text)
    
    result.update({'create_date': extract_date(get_field(text, 'Date'))})
    result.update({'seller': get_field(text, 'From')})
    expense_and_currency = get_cost(text)
    result.update({'total': expense_and_currency[0]})
    result.update({'currency': expense_and_currency[1]})
    
    return result