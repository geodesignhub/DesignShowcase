from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
import nltk
nltk.download('punkt')
def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return None
 
def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None
 
def sentence_similarity(sentence1, sentence2):
    """ compute the sentence similarity using Wordnet """
    # Tokenize and tag
    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))
 
    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]
 
    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]
 
    score, count = 0.0, 0
    best_score = [0.0]
    for ss1 in synsets1:
        for ss2 in synsets2:
            best1_score=ss1.path_similarity(ss2)
            if best1_score is not None:
                best_score.append(best1_score)
        max1=max(best_score)
        if best_score is not None:
            score += max1
            if max1 is not 0.0:
                count += 1
                best_score=[0.0]

    # Average the values
    score /= count
    return score
 
sentences = ['Improve wetland conditions ', 'connect car seq. areas ', 'Farm Trail', 'Critical Trail Connections', 'Richardson ParknRide Trail to rail-trail', 'Extra Bustops', 'Reconstruct existing housing to affordable houses', 'Habitat Corridor Protection Area', 'Connect Protected Areas', 'Beaver Analog Area East Canyon Creek', 'Three Kings Water Treatment Plant', 'Energy Efficient construction requirement', 'PCMC Golf Maintenance Building', 'Conservation Easement (Quarry to Old Ranch)', 'Wildlife Corridor with Potential for Recreation', 'SR 248 Water Transmission Line', 'Deer Crest Pump Station', 'Trout Enhancement ', 'Park City Public Utilities Building', 'Swaner Test Plot on Elk Disturbance and Carbon ', 'Park City Operational Storage', 'Update Land Use Policies to reduce VMT', 'Restore Stream flow for Cutthroat Trout', 'Old rail line trail system extension of H248 ', 'Three Kings to Boothill Water Transmission Line', 'Elk Migration - RV to Swaner', 'Banning Septic Systems in Critical Watershed', 'High Density Housing 3', 'Park meadows to Old Ranch Road Connection ', 'Weatherize existing affordable housing units', 'Grazing for weed control', 'Ban Septic Systems around Jordanelle Watershed', 'high density affordable units', 'Domestic for Waterfowl Nesting', 'Expanded Arts District', 'Stone Ridge Parcel to Old Ranch Road Trailhead ', 'Park City Heights Phase II', "Park & Ride Kimball's Jct.", 'Parking lot trees', 'Develop a Personal Rapid Transit system', 'urban carbon storage policy', 'Grocery/Drug/Gas and Local services', 'Wetland Enhancement', 'Park & Ride Quinns Jct', 'Aspen Measles Burn for Regeneration', 'West Neck Water Tank', 'Grocery/Gas/Drug and Local Services', 'Transfer Station for Recycling and Trash collectio', 'Hi-Ute Ranch Passive Recreation Area (winter use) ', 'Golf Course', 'Expand E-Bike stations', 'Wetland Enhancement - RV', 'Weatherize existing affordable housing units - 2', 'West Neck Water Transmission Line', 'Increase Minimum In stream Flow ', 'Conduit Financing for Ski Resort Infrastructure', 'Bonanza Flat Passive Recreation Area', 'save the forest high density units', 'Dredge & Restore Golf Course Ponds', 'Silver Creek Restoration', 'Hi-Ute All season loop', 'Micro Transit', 'Rehab and upgrade all existing affordable housing', 'Old Ranch Conservation Easement', 'Range Improvement ', 'Jeremy Wildlife and people landbridge', 'small business and affordable unit bonus', 'Robs connection to Hi-ute Ranch', 'Food Truck Hub', 'OPEN SPACE - BITNER FARM', 'Hi-Ute Flat to Pinebrook Single Track Trail', 'Millennium Trail to Hi-Ute Loop ', 'Bitner Conservation Easement', 'Unused lawns into community gardens', 'Hi-Ute Flat to Pinebrook Single Track Trail #2', 'Deer Crest to Bald Eagle Water Transmission Line', 'EAST CANYON CREEK WETLAND/RIPARIAN IMPROVEMENT', 'Managing Ski Runs to better store Carbon', 'Willow Regeneration', 'Bridge Connecting Rail Trail to BOPA', 'building with solar energy capabilities', 'HIKING ONLY TRAIL CONNECTION RASSMUSEN OS', 'Bitner Elk Corridoor', 'Roundabout and tunnel Kearns Blvd', 'Biofuels Refinery', 'Grazing for weed control', 'Trail to Connect Poison Creek with McCloud Creek', 'Field House Ice Rink Bonaza Park', 'Conect Jordenell Village to Deercrest Gondola ', 'Golf Course enhancement to Multi-use', 'Ecker Hill Park and Ride Lot, Transit Connect,', 'Elk and Deer Hunting', 'High Density Housing 1', 'Scenic Bikeway Designation', 'Richardson Flat Wetland/Waterway/Meadow Restore', 'No pure residential housing projects', 'High Density Affordable Housing 2', 'Low density affordable housing']

focus_sentence = "Reconstruct existing housing to affordable houses"
 
for sentence in sentences:
    print("Similarity(\"%s\", \"%s\") = %s" % (focus_sentence, sentence, sentence_similarity(focus_sentence, sentence)))
    print("Similarity(\"%s\", \"%s\") = %s" % (sentence, focus_sentence, sentence_similarity(sentence, focus_sentence)))
    # print 
 
# Similarity("Cats are beautiful animals.", "Dogs are awesome.") = 0.511111111111
# Similarity("Dogs are awesome.", "Cats are beautiful animals.") = 0.666666666667
 
# Similarity("Cats are beautiful animals.", "Some gorgeous creatures are felines.") = 0.833333333333
# Similarity("Some gorgeous creatures are felines.", "Cats are beautiful animals.") = 0.833333333333
 
# Similarity("Cats are beautiful animals.", "Dolphins are swimming mammals.") = 0.483333333333
# Similarity("Dolphins are swimming mammals.", "Cats are beautiful animals.") = 0.4
 
# Similarity("Cats are beautiful animals.", "Cats are beautiful animals.") = 1.0
# Similarity("Cats are beautiful animals.", "Cats are beautiful animals.") = 1.0
 