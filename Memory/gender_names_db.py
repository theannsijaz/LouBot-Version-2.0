"""
Gender Detection Names Database
==============================

Contains English and Pakistani names for gender detection during user signup.
Default behavior: If no match found, assigns "Male" as default gender.
"""

# English Male Names (100)
ENGLISH_MALE_NAMES = {
    'james', 'robert', 'john', 'michael', 'david', 'william', 'richard', 'joseph',
    'thomas', 'christopher', 'charles', 'daniel', 'matthew', 'anthony', 'mark', 'donald',
    'steven', 'paul', 'andrew', 'joshua', 'kenneth', 'kevin', 'brian', 'george',
    'timothy', 'ronald', 'jason', 'edward', 'jeffrey', 'ryan', 'jacob', 'gary',
    'nicholas', 'eric', 'jonathan', 'stephen', 'larry', 'justin', 'scott', 'brandon',
    'benjamin', 'samuel', 'frank', 'raymond', 'alexander', 'patrick', 'jack', 'dennis',
    'jerry', 'tyler', 'aaron', 'jose', 'henry', 'adam', 'douglas', 'nathaniel',
    'peter', 'zachary', 'kyle', 'noah', 'alan', 'ethan', 'jeremy', 'lionel',
    'arthur', 'mason', 'wayne', 'ralph', 'roy', 'eugene', 'louis', 'walter',
    'jordan', 'albert', 'sean', 'harold', 'craig', 'philip', 'carl', 'roger',
    'keith', 'marcus', 'francis', 'dean', 'lucas', 'martin', 'felix', 'oscar',
    'bruce', 'billy', 'freddie', 'harvey', 'victor', 'austin', 'leo', 'clark',
    'gilbert', 'bernard', 'chester', 'floyd', 'curtis', 'anns'
}

# English Female Names (100)
ENGLISH_FEMALE_NAMES = {
    'mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan', 'jessica',
    'sarah', 'karen', 'nancy', 'lisa', 'betty', 'helen', 'sandra', 'donna',
    'carol', 'ruth', 'sharon', 'michelle', 'laura', 'sarah', 'kimberly', 'deborah',
    'dorothy', 'lisa', 'nancy', 'karen', 'betty', 'helen', 'sandra', 'donna',
    'emily', 'margaret', 'ashley', 'emma', 'olivia', 'sophia', 'ava', 'isabella',
    'mia', 'abigail', 'madison', 'charlotte', 'harper', 'sofia', 'avery', 'ella',
    'scarlett', 'grace', 'chloe', 'victoria', 'riley', 'aria', 'lily', 'aubrey',
    'zoey', 'penelope', 'lillian', 'addison', 'layla', 'natalie', 'camila', 'hannah',
    'brooklyn', 'zoe', 'nora', 'leah', 'savannah', 'audrey', 'claire', 'eleanor',
    'skylar', 'ellie', 'samantha', 'stella', 'paisley', 'violet', 'mila', 'allison',
    'alice', 'madelyn', 'julia', 'ruby', 'lucy', 'anna', 'caroline', 'genesis',
    'aaliyah', 'kennedy', 'kinsley', 'maya', 'naomi', 'elena', 'gabriella', 'ariana',
    'lauren', 'leilani', 'jasmine', 'nicole', 'amy'
}

# Pakistani Male Names (100) 
PAKISTANI_MALE_NAMES = {
    'muhammad', 'ahmed', 'ali', 'hassan', 'hussain', 'omar', 'abdullah', 'ibrahim',
    'usman', 'bilal', 'tariq', 'imran', 'kamran', 'fahad', 'waqar', 'shahid',
    'adnan', 'salman', 'faisal', 'danish', 'asif', 'saad', 'hamza', 'zain',
    'malik', 'awais', 'kashif', 'omer', 'sohail', 'nasir', 'zahid', 'iqbal',
    'rashid', 'amjad', 'sajjad', 'junaid', 'shafiq', 'naeem', 'khalid', 'farhan',
    'yasir', 'rizwan', 'tanvir', 'qasim', 'nabeel', 'waseem', 'shakeel', 'saleem',
    'haider', 'javed', 'mansoor', 'asad', 'akram', 'hanif', 'raza', 'azeem',
    'babar', 'shoaib', 'majid', 'masood', 'ghulam', 'pervez', 'rafiq', 'arshad',
    'mohsin', 'zaheer', 'anwar', 'akbar', 'jamil', 'karim', 'sabir', 'bashir',
    'naveed', 'tahir', 'wajid', 'shahbaz', 'mushtaq', 'amin', 'saeed', 'nadeem',
    'aslam', 'ashraf', 'waheed', 'shaukat', 'altaf', 'yousaf', 'ishaq', 'idrees',
    'asim', 'azhar', 'mubarak', 'safdar', 'ismail', 'haroon', 'mudassir', 'noman',
    'shahzad', 'zeeshan', 'sameer', 'waleed', 'mehmood', 'sajid', 'sajjad', 'hussain'
}

# Pakistani Female Names (100)
PAKISTANI_FEMALE_NAMES = {
    'fatima', 'aisha', 'khadija', 'zainab', 'maryam', 'ruqayyah', 'hafsa', 'saima',
    'nadia', 'sana', 'farah', 'asma', 'hina', 'rabia', 'samina', 'shazia',
    'uzma', 'shabnam', 'nasreen', 'ambreen', 'tahira', 'rubina', 'fouzia', 'shahnaz',
    'sadia', 'bushra', 'rimsha', 'ayesha', 'maria', 'sidra', 'kinza', 'amna',
    'iqra', 'mahnoor', 'mehwish', 'sahar', 'laiba', 'javeria', 'zara', 'arooba',
    'maheen', 'nayab', 'tehreem', 'areeba', 'aliza', 'mahira', 'eman', 'rida',
    'dua', 'anaya', 'zoya', 'aleena', 'hareem', 'maira', 'arisha', 'haniya',
    'sania', 'nimra', 'yumna', 'sara', 'momina', 'fatimah', 'hajira', 'ifra',
    'palwasha', 'gulnar', 'noor', 'sundus', 'samra', 'amber', 'zunera', 'anam',
    'salma', 'naseem', 'kiran', 'rashida', 'jamila', 'sultana', 'parveen', 'yasmeen',
    'shamim', 'rehana', 'razia', 'farida', 'zahida', 'shahida', 'sajida', 'rashida',
    'farzana', 'rukhsana', 'shaheen', 'nargis', 'anisa', 'humera', 'amina', 'lubna',
    'tayyaba', 'shagufta', 'musarrat', 'muskan'
}

def detect_gender_from_name(name):
    """
    Detect gender based on name comparison with database.
    
    Args:
        name (str): First name to analyze
        
    Returns:
        str: 'Male', 'Female', or 'Male' (default if no match)
    """
    if not name:
        return 'Male'  # Default fallback
    
    # Clean and normalize the name
    clean_name = name.strip().lower()
    
    # Extract first name if full name is provided
    first_name = clean_name.split()[0] if ' ' in clean_name else clean_name
    
    # Check against all name databases
    if first_name in ENGLISH_MALE_NAMES or first_name in PAKISTANI_MALE_NAMES:
        return 'Male'
    elif first_name in ENGLISH_FEMALE_NAMES or first_name in PAKISTANI_FEMALE_NAMES:
        return 'Female'
    else:
        # Default to Male if no match found
        return 'Male'

def get_all_male_names():
    """Returns set of all male names for reference."""
    return ENGLISH_MALE_NAMES.union(PAKISTANI_MALE_NAMES)

def get_all_female_names():
    """Returns set of all female names for reference."""
    return ENGLISH_FEMALE_NAMES.union(PAKISTANI_FEMALE_NAMES)

def get_database_stats():
    """Returns statistics about the names database."""
    return {
        'english_male': len(ENGLISH_MALE_NAMES),
        'english_female': len(ENGLISH_FEMALE_NAMES),
        'pakistani_male': len(PAKISTANI_MALE_NAMES),
        'pakistani_female': len(PAKISTANI_FEMALE_NAMES),
        'total_male': len(get_all_male_names()),
        'total_female': len(get_all_female_names()),
        'total_names': len(get_all_male_names()) + len(get_all_female_names())
    }

# Example usage and testing
if __name__ == "__main__":
    test_names = [
        "Muhammad", "Fatima", "John", "Mary", "Hassan", "Aisha",
        "Michael", "Sarah", "Unknown Name", "Ali", "Jennifer"
    ]
    
    print("Gender Detection Test:")
    print("=" * 30)
    for test_name in test_names:
        detected_gender = detect_gender_from_name(test_name)
        print(f"{test_name:15} -> {detected_gender}")
    
    print(f"\nDatabase Statistics:")
    print("=" * 30)
    stats = get_database_stats()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title():15}: {value}") 