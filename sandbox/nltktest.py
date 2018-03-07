
# Imports
import difflib
import nltk

# Imports
import nltk.corpus
import nltk.tokenize.punkt
import nltk.stem.snowball
import string

from nltk.corpus import wordnet

nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


target_sentence = "Reconstruct existing housing to affordable houses"

sentences = ['Improve wetland conditions ', 'connect car seq. areas ', 'Farm Trail', 'Critical Trail Connections', 'Richardson ParknRide Trail to rail-trail', 'Extra Bustops', 'Reconstruct existing housing to affordable houses', 'Habitat Corridor Protection Area', 'Connect Protected Areas', 'Beaver Analog Area East Canyon Creek', 'Three Kings Water Treatment Plant', 'Energy Efficient construction requirement', 'PCMC Golf Maintenance Building', 'Conservation Easement (Quarry to Old Ranch)', 'Wildlife Corridor with Potential for Recreation', 'SR 248 Water Transmission Line', 'Deer Crest Pump Station', 'Trout Enhancement ', 'Park City Public Utilities Building', 'Swaner Test Plot on Elk Disturbance and Carbon ', 'Park City Operational Storage', 'Update Land Use Policies to reduce VMT', 'Restore Stream flow for Cutthroat Trout', 'Old rail line trail system extension of H248 ', 'Three Kings to Boothill Water Transmission Line', 'Elk Migration - RV to Swaner', 'Banning Septic Systems in Critical Watershed', 'High Density Housing 3', 'Park meadows to Old Ranch Road Connection ', 'Weatherize existing affordable housing units', 'Grazing for weed control', 'Ban Septic Systems around Jordanelle Watershed', 'high density affordable units', 'Domestic for Waterfowl Nesting', 'Expanded Arts District', 'Stone Ridge Parcel to Old Ranch Road Trailhead ', 'Park City Heights Phase II', "Park & Ride Kimball's Jct.", 'Parking lot trees', 'Develop a Personal Rapid Transit system', 'urban carbon storage policy', 'Grocery/Drug/Gas and Local services', 'Wetland Enhancement', 'Park & Ride Quinns Jct', 'Aspen Measles Burn for Regeneration', 'West Neck Water Tank', 'Grocery/Gas/Drug and Local Services', 'Transfer Station for Recycling and Trash collectio', 'Hi-Ute Ranch Passive Recreation Area (winter use) ', 'Golf Course', 'Expand E-Bike stations', 'Wetland Enhancement - RV', 'Weatherize existing affordable housing units - 2', 'West Neck Water Transmission Line', 'Increase Minimum In stream Flow ', 'Conduit Financing for Ski Resort Infrastructure', 'Bonanza Flat Passive Recreation Area', 'save the forest high density units', 'Dredge & Restore Golf Course Ponds', 'Silver Creek Restoration', 'Hi-Ute All season loop', 'Micro Transit', 'Rehab and upgrade all existing affordable housing', 'Old Ranch Conservation Easement', 'Range Improvement ', 'Jeremy Wildlife and people landbridge', 'small business and affordable unit bonus', 'Robs connection to Hi-ute Ranch', 'Food Truck Hub', 'OPEN SPACE - BITNER FARM', 'Hi-Ute Flat to Pinebrook Single Track Trail', 'Millennium Trail to Hi-Ute Loop ', 'Bitner Conservation Easement', 'Unused lawns into community gardens', 'Hi-Ute Flat to Pinebrook Single Track Trail #2', 'Deer Crest to Bald Eagle Water Transmission Line', 'EAST CANYON CREEK WETLAND/RIPARIAN IMPROVEMENT', 'Managing Ski Runs to better store Carbon', 'Willow Regeneration', 'Bridge Connecting Rail Trail to BOPA', 'building with solar energy capabilities', 'HIKING ONLY TRAIL CONNECTION RASSMUSEN OS', 'Bitner Elk Corridoor', 'Roundabout and tunnel Kearns Blvd', 'Biofuels Refinery', 'Grazing for weed control', 'Trail to Connect Poison Creek with McCloud Creek', 'Field House Ice Rink Bonaza Park', 'Conect Jordenell Village to Deercrest Gondola ', 'Golf Course enhancement to Multi-use', 'Ecker Hill Park and Ride Lot, Transit Connect,', 'Elk and Deer Hunting', 'High Density Housing 1', 'Scenic Bikeway Designation', 'Richardson Flat Wetland/Waterway/Meadow Restore', 'No pure residential housing projects', 'High Density Affordable Housing 2', 'Low density affordable housing']

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)
stopwords.append('')

stemmer = nltk.stem.snowball.SnowballStemmer('english')
def is_ci_partial_seq_token_stopword_lemma_match(a, b):
    """Check if a and b are matches."""
    pos_a = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(a)))
    pos_b = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(b)))
    lemmae_a = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a \
                    if token.lower().strip(string.punctuation) not in stopwords]
    lemmae_b = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b \
                    if token.lower().strip(string.punctuation) not in stopwords]

    # Create sequence matcher
    s = difflib.SequenceMatcher(None, lemmae_a, lemmae_b)
    return (s.ratio() > 0.66)

def is_ci_token_stopword_lemma_match(a, b):
    """Check if a and b are matches."""
    pos_a = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(a)))
    pos_b = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(b)))
    lemmae_a = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a \
                    if token.lower().strip(string.punctuation) not in stopwords]
    lemmae_b = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b \
                    if token.lower().strip(string.punctuation) not in stopwords]

    return (lemmae_a == lemmae_b)
def get_wordnet_pos(pos_tag):
    if pos_tag[1].startswith('J'):
        return (pos_tag[0], wordnet.ADJ)
    elif pos_tag[1].startswith('V'):
        return (pos_tag[0], wordnet.VERB)
    elif pos_tag[1].startswith('N'):
        return (pos_tag[0], wordnet.NOUN)
    elif pos_tag[1].startswith('R'):
        return (pos_tag[0], wordnet.ADV)
    else:
        return (pos_tag[0], wordnet.NOUN)

# Create tokenizer and stemmer
tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

def is_ci_token_stopword_stem_match(a, b):
    """Check if a and b are matches."""
    tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a) \
                    if token.lower().strip(string.punctuation) not in stopwords]
    tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b) \
                    if token.lower().strip(string.punctuation) not in stopwords]
    stems_a = [stemmer.stem(token) for token in tokens_a]
    stems_b = [stemmer.stem(token) for token in tokens_b]

    return (stems_a == stems_b)

def is_ci_token_stopword_match(a, b):
    """Check if a and b are matches."""
    tokens_a = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(a) \
                    if token.lower().strip(string.punctuation) not in stopwords]
    tokens_b = [token.lower().strip(string.punctuation) for token in tokenizer.tokenize(b) \
                    if token.lower().strip(string.punctuation) not in stopwords]
    
    return (tokens_a == tokens_b)

def is_ci_partial_noun_set_token_stopword_lemma_match(a, b):
    """Check if a and b are matches."""
    pos_a = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(a)))
    pos_b = map(get_wordnet_pos, nltk.pos_tag(tokenizer.tokenize(b)))
    lemmae_a = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a \
                    if pos == wordnet.NOUN and token.lower().strip(string.punctuation) not in stopwords]
    lemmae_b = [lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b \
                    if pos == wordnet.NOUN and token.lower().strip(string.punctuation) not in stopwords]

    # Calculate Jaccard similarity
    ratio = len(set(lemmae_a).intersection(lemmae_b)) / float(len(set(lemmae_a).union(lemmae_b)))
    return (ratio > 0.66)

for sentence in sentences:
   print(is_ci_token_stopword_match(target_sentence, sentence), sentence)