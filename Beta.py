import re


####################### ####################
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

###################### GET CREATOR ##################
def get_creator(text):
    KEY_FIELDS = ['created_by:', 'created by:']
    email_regexes = [r"[a-z][a-z0-9_\.]{5,32}@[a-z0-9]{2,}(\.[a-z0-9]{2,4}){1,2}", \
                   r" ,"]
    
    
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


###################### GET DATE #####################
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
    if substring_found:
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


###################### GET VENDOR #######################
def count(text, word):
    if len(word)==0:
        return 0
    return len(re.findall(word, text, re.IGNORECASE))


def preprocess_and_split_email(rear_part):
    result = []
    result = rear_part.split(".")
    return result


def get_vendor_via_email(text, email):
    if "@" not in email:
        return ""
    rear_part = email[re.search("@", email).end():]
    result = ""
    max_count = 0
    strings = preprocess_and_split_email(rear_part)
    
    for i in range(len(strings)-1):
        string = strings[i]
        tmp = count(text, string)
        if max_count<tmp:
            max_count=tmp
            result = string
            
    return result


def get_vendor(text):
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
        
        if len(name)>0:
            return name
        else:
            return get_vendor_via_email(text, email)
    
    return ""


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


##################### GET COST #######################
def string_to_float(numstring):
    """
        convert a string with splitter ','' and '.' to float
    """
#     print(numstring)
    result = 0
    tmp = 0
    begin = 0
    end = len(numstring)
    if len(numstring)>2:
        if not re.match(r"\d{1}", numstring[-3]):
            tmp = tmp + int(numstring[-2])/10 + int(numstring[-1])/100
            end = end - 3
        
    for i in range(begin, end):
        if re.match(r"\d{1}", numstring[i]):
            result = result*10 + int(numstring[i])
            
    return result + tmp

def get_currency(text, cost_begin, cost_end, currency_radius=5):
    CURRENCIES = {'[$]':'Dollar', 'USD':'Dollar', 'VND|vnd':'VND', '₫':'VND', 'đ':'VND'}
    for currency in CURRENCIES.keys():
        if re.search(currency, text[max(cost_begin-currency_radius, 0): \
                                    min(cost_end+currency_radius, len(text))]):
            return CURRENCIES[currency]
    return ""

def choose_between_cost_founds(cost_tuple1, cost_tuple2):
    if not cost_tuple1:
        return cost_tuple2
    if not cost_tuple2:
        return cost_tuple1
    
    position1 = cost_tuple1[1]
    position2 = cost_tuple2[1]
    currency1 = cost_tuple1[2]
    currency2 = cost_tuple2[2]
    
    if not (len(currency1)*len(currency2)==0):
        if position1>position2:
            return cost_tuple1
        else:
            return cost_tuple2
    else:
        if len(currency1)>0:
            return cost_tuple1
        else:
            return cost_tuple2
        
        
def get_cost_by_cost_regex_and_keyword(text, cost_regex, keyword):
    keyword_found = list(re.finditer(keyword, text, re.IGNORECASE))
    left = 0
    result = None
    for i in range(len(keyword_found)):
        match = keyword_found[i]
        if i==0:
            left = match.end()
        else:
            right = match.start()
            cost_found = re.search(cost_regex, text[left:right])
            if cost_found:
                currency = get_currency(text, left + cost_found.start(), left + cost_found.end())
                tmp = (cost_found.group(), left + cost_found.start(), currency)
                result = choose_between_cost_founds(result, tmp)
            left = match.end()
    if len(keyword_found)>0:
        cost_found = re.search(cost_regex, text[left:-1])
        if cost_found:
            currency = get_currency(text, left + cost_found.start(), left + cost_found.end())
            tmp = (cost_found.group(), left + cost_found.start(), currency)
            result = choose_between_cost_founds(result, tmp)
    return result

def get_cost_by_cost_regex(text, cost_regex):
    KEYWORDS = ['amount paid', 'amount', 'charged', 'total payment', 'total', 'you paid', \
                'thanh toán', 'tổng cộng', 'tổng', 'số tiền', 'thanh toan', 'tong cong', 'tong', 'so tien']
    
    result = None
    for keyword in KEYWORDS:
        tmp = get_cost_by_cost_regex_and_keyword(text, cost_regex, keyword)
        result = choose_between_cost_founds(result, tmp)
#         if tmp and ((not result) or (result and result[1]<tmp[1])):
#             result = tmp
            
    return result
                
                
def get_cost(text):
    COST_REGEXES = [r'(?<!([,\d]))(\d{1,3})([,]\d{3})+([.]\d{2})?(?!\d)', \
                    r'(?<!([.\d]))(\d{1,3})([.]\d{3})+([,]\d{2})?(?!\d)', \
                    r'\d+([.,]\d{2})?(?!\d)']
#                     r'(?<![,\d])\d+([,]\d{2})?(?!\d)', \
#                     r'(?<![.\d])\d+([.]\d{2})?(?!\d)']    
    
    for cost_regex in COST_REGEXES:
        cost_found = get_cost_by_cost_regex(text, cost_regex)
        if cost_found:
            expense = string_to_float(cost_found[0])
            currency = get_currency(text, cost_found[1], cost_found[1] + len(cost_found[0]))
            return expense, currency
        
     
    return (0, "")

############# MAIN FUNCTION ###############
def extract_from_email_bodytext(text):
    """
        from body text of the email, extract the information
    """   
    result = {}
    result.update({'created_by': get_creator(text)})
    text = truncate(text)
    
    result.update({'date': get_date(text)})
    result.update({'seller': get_vendor(text)})
    expense_and_currency = get_cost(text)
    result.update({'total': expense_and_currency[0]})
    result.update({'currency': expense_and_currency[1]})
    
    return result