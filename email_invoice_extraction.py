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
    begin_keyword = "From:|Từ:"
    check_regex = r"(From:|Từ:).+[@].+(Date:|Ngày:)"
    
    tmp = 0
    while True:
        # Find the last "From" to get the exact location of seller information
        from_found = re.search(begin_keyword, text[tmp:])
        if from_found and re.match(check_regex, text[tmp+from_found.start():]):
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


def preprocess_and_split_datestring(datestring):
    result = []
    datestring = datestring.replace(",", "")
    result = datestring.split()
    return result


def is_eng_date(datestring):
    weekday_dict = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return datestring[:3] in weekday_dict


def is_vie_date(datestring):
    pass


def extract_eng_date(datestring):
    """
        get the day, month, year in the english datestring
    """
        
    month_dict = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', \
                  'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    tokens = preprocess_and_split_datestring(datestring)
    
    year = ''
    month = ''
    day = ''
    
    yearregex = r'(19|20)\d{2}'
    dayregex = r'([12]\d|3[01]|0?[1-9])'
    
    for token in tokens:
        """
            loop over all the integer in the string to check if it is day or month or year
        """
        if (month=='') and (token in month_dict):
            month = month_dict[token]
        elif (day=='') and re.match(dayregex, token):
            day = token
        elif (year=='') and re.match(yearregex, token):
            year = token
            
    if len(day)==1:
        day = '0' + day
    return day + '/' + month + '/' + year


def extract_vie_date(datestring):
    """
        get the day, month, year in the english datestring
    """
    substring_found = re.search(r",.+,.+", datestring)
    datestring = substring_found.group()
    tokens = preprocess_and_split_datestring(datestring)
    
    year = ''
    month = ''
    day = ''
    
    yearregex = r'(19|20)\d{2}'
    monthregex = r'(1[012]|0?[1-9])'
    dayregex = r'([12]\d|3[01]|0?[1-9])'
    
    for token in tokens:
        """
            loop over all the integer in the string to check if it is day or month or year
        """
        if (day=='') and re.match(dayregex, token):
            day = token
        elif (month=='') and re.match(monthregex, token):
            month = token
        elif (year=='') and re.match(yearregex, token):
            year = token
            
    if len(day)==1:
        day = '0' + day
    if len(month)==1:
        month = '0' + month
    return day + '/' + month + '/' + year


def extract_date(datestring):
    if is_eng_date(datestring):
        return extract_eng_date(datestring)
    else:
        return extract_vie_date(datestring)
    

def get_date(text):
    """
        Get date from the text
    """
    FIELDS = ['From|Từ', 'Subject|Chủ đề', 'Date|Ngày', 'To|Tới']
    key_field = 'Date|Ngày'
    
    begin = 0
    end = len(text)
    
    found = re.search(key_field, text[begin:end], re.IGNORECASE)
    if found:
        # search for the key_field (begin point of result)
        begin = begin + found.end()
        if text[begin]==':':
            begin += 1
            
        for field in FIELDS:
            # search for the other fields (end point of result)
            endfound = re.search(field, text[begin:end], re.IGNORECASE)
            if endfound:
                # update the endpoint (the closest field to the key_field)
                end = min(end, begin + endfound.start())
    
    return extract_date(text[begin:end].strip())


def longest_common_substring(str1, str2):
    from difflib import SequenceMatcher
    str1 = str1.upper()
    str2 = str2.upper()
    seqMatch = SequenceMatcher(None, str1, str2)
    match = seqMatch.find_longest_match(0, len(str1), 0, len(str2))
    return str1[match.a: match.a + match.size]


def get_seller(text):
    """
        Get seller information from the text
    """
    result = ""
    
    FIELDS = ['From|Từ', 'Subject|Chủ đề', 'Date|Ngày', 'To|Tới']
    key_field = 'From|Từ'
    
    email_regex = r"<.+>"
    begin = 0
    end = len(text)
    
    found = re.search(key_field, text[begin:end], re.IGNORECASE)
    if found:
        # search for the key_field (begin point of result)
        begin = begin + found.end()
        if text[begin]==':':
            begin += 1
            
        for field in FIELDS:
            # search for the other fields (end point of result)
            endfound = re.search(field, text[begin:end], re.IGNORECASE)
            if endfound:
                # update the endpoint (the closest field to the key_field)
                end = min(end, begin + endfound.start())
    
    result = text[begin:end].strip()
    
    email_found = re.search(email_regex, result)
    if email_found:
        email = result[email_found.start() : email_found.end()]
        email = email[1:-1]    # get rid of the pair of brackets surrounding the email string
        name = result[:email_found.start()].strip()
        
        if len(name)==0:
            name = longest_common_substring(email, get_subject(text))
        return name
    
    return result


def get_subject(text):
    """
        Get the subject of the email
    """
    FIELDS = ['From|Từ', 'Subject|Chủ đề', 'Date|Ngày', 'To|Tới']
    key_field = 'Subject|Chủ đề'
    
    begin = 0
    end = len(text)
    
    found = re.search(key_field, text[begin:end], re.IGNORECASE)
    if found:
        # search for the key_field (begin point of result)
        begin = begin + found.end()
        if text[begin]==':':
            begin += 1
            
        for field in FIELDS:
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
    CURRENCIES = {'[$]':'Dollar', 'USD':'Dollar', 'VND':'VND', '₫':'VND', 'đ':'VND'}
    for currency in CURRENCIES.keys():
        if re.search(currency, string, re.IGNORECASE):
            return CURRENCIES[currency]
    return ""


def get_cost(text):
    """
        get the total cost in the text
    """
    KEYWORDS = ['total', 'amount paid', 'amount', 'charged', 'total payment', 'you paid', 'tổng', \
                'tổng cộng', 'số tiền', 'thanh toán', 'tong', 'tong cong', 'so tien', 'thanh toan']   
    VI_COST_REGEXES = [r'\d{1,3}([.]\d{3})+([,]\d{2})?', r'\d+([,]\d{2})?']
    EN_COST_REGEXES = [r'\d{1,3}([,]\d{3})+([.]\d{2})?', r'\d+([.]\d{2})?']
    
    expense = 0
    currency = ""
    
    begin = 0
    end = len(text)
    
    tmp = 0
    for keyword in KEYWORDS: 
        # search for keyword, which is followed by the total cost
        while True:
            keyword_found = re.search(keyword, text[tmp:], re.IGNORECASE)
            if keyword_found:
#                 print(keyword_found)
                tmp = tmp + keyword_found.end()
            else:
                break
    
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


def get_creator(text):
    KEY_FIELDS = ['created_by', 'Created by', 'created by']
    email_regexes = [r"[a-z][a-z0-9_\.]{5,32}@[a-z0-9]{2,}(\.[a-z0-9]{2,4}){1,2}", \
                   r"[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*"]
    
    
    begin = 0
    end = len(text)
    
    for key_field in KEY_FIELDS:        
        found = re.search(key_field, text[begin:end], re.IGNORECASE)
        if found:
            # search for the key_field (begin point of result)
            begin = begin + found.end()
            for regex in email_regexes:
                creator_found = re.search(regex, text[begin:])
                if creator_found:
                    return text[begin+creator_found.start() : begin+creator_found.end()].strip()
        
    return ""


def extract_from_email_bodytext(text):
    """
        from body text of the email, extract the information
    """   
    result = {}
    result.update({'created_by': get_creator(text)})
    text = truncate(text)
    
    result.update({'date': get_date(text)})
    result.update({'seller': get_seller(text)})
    expense_and_currency = get_cost(text)
    result.update({'total': expense_and_currency[0]})
    result.update({'currency': expense_and_currency[1]})
    
    return result
