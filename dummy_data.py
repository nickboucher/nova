#!/usr/bin/env python3
#
# dummy_data.py
# Nicholas Boucher 2017
#
# Contains a script that populates the NOVA database
# with dummy data that is useful for testing via HTTP
# requests.
#
from random import uniform, choice, randrange
from requests import get
from urllib.parse import quote
from sys import exit

# A list of all clubs on campus
clubs = ["Act On A Dream","Africa Business and Investment Club (HABIC)","African Students Association (HASA)","Aikikai","Alzheimer's Buddies","Anime Society","Archery","Armenian Students Association","Asian American Association (AAA)","Asian American Brotherhood (AAB)","Asian American Dance Troupe (AADT)","Asian American Women's Association","Asian Baptist Student Koinonia (ABSK)","Association for the Promotion of Interplanetary Expansion (HAPIE)","Association for U.S.-China Relations (HAUSCR)","Association of Black Harvard Women (ABHW)","Athena Conference","Bach Society Orchestra (BachSoc)","Badminton","Baha'i Association","Ballet Company","Ballroom Dance","Ballroom Dance Team (HBDT)","Baroque Chamber Orchestra","Baseball","Beekeepers","Bhangra","Billiards","Biomedical Engineering Society (BMES)","Biotechnology Association","Black Community and Student Theater Group (BlackC.A.S.T.)","Black Men's Forum (BMF)","Black Pre-Law Association (BPLA)","Black Students Association (BSA)","Book Review","Bowling","Boxing","Brattle Street Chamber Players","Brazilian Association (HUBA)","Breakers","British Club","Broomball","Bulgarian Club","BWISE: BSC Fellows for a Whole Integrated Student Experience","Canadian Club","Candela Dance Troupe","Capoeira","Caribbean Club","Catholic Student Association (CSA)","Chado Society","Cheerleading","Chess Club","China Forum (HCCF)","Chinese Music Ensemble (HCME)","Chinese Students Association (CSA)","Christian Impact","Christians on Campus","CityStep","Climbing","Coalition for East African Peace","College Bowl","College Events Board","Collegium","Colombian Students Association","Community Garden","Community of Humanists, Atheists, and Agnostics","Composers Association","Computer Society (HCS)","Concilio Latino","Consent Advocates and Relationship Educators (CARE)","Consulting Group (HCCG)","Consulting on Business and the Environment","Contact Peer Counseling","Convrgency","Cornhole","Cricket","Crimson","Crimson Dance","Crimson Key Society (CKS)","CrimsonEMS","Crunch Magazine","Cuban-American Undergraduate Student Association (CAUSA)","Cube Club","Curling","Cycling","Dancing to Heal","Data Ventures","Debate Council","Debating Union","Deepam","Democrats","Developers for Development","Development Think Tank","Dharma","Digital Literacy Project","Din & Tonics","DirecTutor","Disability Alliance","DREAM","Dreamporte","Drug and Alcohol Peer Advisors (DAPA)","Eating Concerns Hotline and Outreach (ECHO)","Ecdysis","Ecomarathon Team","Economics Association","Economics Review","Effective Altruism","Electronic Music Collective","Eleganza","Engineering Society (HCES)","Engineers Without Borders (EWB)","Episcopal Students","eSports Association","European Business Group","European Society","Evening with Champions","Expressions","Faith and Action (HCFA)","Fallen Angels","Fencing","Field Hockey","Figure Skating","Film Festival","Financial Analysts Club","First Generation Student Union","First-Year Outdoor Program (FOP)","First-Year Social Committee (FYSC)","Flute Ensemble","Food Lab for Kids","Food Literacy Project","Foundation for International Medical Relief of Children (FIMRC)","Francophone Society","Franklin Fellowship","Friends of Project Sunshine","Fuerza Latina","FUSIAN","Futsal","Future Surgeons","G-Chat: First-Year Discussion Group","Gender Inclusivity in Math","Geological Society","Gilbert & Sullivan Players (HRG&SP)","Glee Club","Global Health and AIDS Coalition","Global Health Forum (HUGHF)","Golf","Green Medicine Initiative","HackHarvardCollege","Haitian Alliance","Half Asian People's Association (HAPA)","Hapkido","Harvard College Coaches","Harvard Organization for Latin America (HOLA)","Harvard Undergraduate BGLTQ Business Society (HUBBS)","Harvard Undergraduates Raising Autism Awareness! (HURAA!)","Harvard University Band","Harvard-Radcliffe Orchestra (HRO)","Hasty Pudding Theatricals (HPT)","HBASIS (Harvard College Bisexual, Gay, Lesbian, Transgender, Queer & Allied Students in the Sciences)","Healing Thoughts","Health Advocacy Program (HAP)","Health Leads","Healthcare Associates","HealthPALs - Health Peer Advisors & Liaisons","High-Tech & Business Group","Hillel","History Club","Holoimua O Hawaii","Hong Kong Society","Honor Council","House and Neighborhood Development (HAND)","HRDC (Harvard--Radcliffe Dramatic Club)","Human Rights in North Korea (HRiNK)","Human Rights Review","Humanities Initiative","Hyperion Shakespeare Company","IDENTITIES Fashion Show","iGEM","Immediate Gratification Players (IGP)","Impact Investing Group","Indigo Peer Counseling","Institute of Politics (IOP)","Interfaith Forum","International Negotiation Program","International Relations Council (IRC)","International Relations on Campus","International Review","International Women's Rights Collective (IWRC)","Iranian Association","Islamic Society (HIS)","Israel Public Affairs","Japan Initiative","Jazz Bands","Jiu Jitsu","John Adams Society","Kendo","KeyChange","Kidney Disease Screening and Awareness Program (KDSAP)","Korean Adoptee Mentorship Program","Krav Maga","La Organizacion de Puertorriquenos en Harvard","Latino Men's Collective (LMC)","Latinos in Health Careers","Latter-day Saint Student Association (LDSSA)","Law Society","Leadership Institute at Harvard College (LIHC)","Lowell House Opera Society","Lowell House Society of Russian Bell Ringers","LowKeys","Manifesta Magazine","Mathematics Association (HUMA)","Medical Humanities Forum","Men's Basketball (Crimson Classics)","Men's Basketball (Harvard Hoopsters)","Men's Ice Hockey","Men's Lacrosse","Men's Rugby","Men's Soccer","Men's Tennis","Mentors for Urban Debate","Mirch","Mock Trial","Model Congress San Francisco","Model United Nations (HMUN)","Modern Dance Company (HRMDC)","Mountaineering Club","Music in Hospitals and Nursing Homes Using Entertainment as Therapy (MIHNUET)","National Model United Nations (HNMUN)","Naturalist Club","Nordic Skiing","Noteables-Harvard's Broadway Beat","Ocean Sciences Club","On Harvard Time (OHT)","Open Philosophy Organization","Opportunes","Organ Society","Organization of Asian American Sisters in Service","Orthodox Christian Fellowship","Outing Club","Palestine Solidarity Committee (PSC)","Pan-African Dance and Music Ensemble (PADAME)","Partners in Health Engage","Passus: Harvard College Step Team","Philippine Forum","Photography Club","Piano Society","Pistol","Polish Society","Political Review (HPR)","Polo","Pops Orchestra","Powerlifting","Pre-Medical Society","Pre-Veterinary Society","Program for International Education (HPIE)","Progressive Jewish Alliance (PJA)","Project for Asian and International Relations (HPAIR)","Project SWIM","Quad Sound Studios (QSS)","Quantitative Trading Club","Quidditch","Radcliffe Choral Society (RCS)","Radcliffe Pitches","Radcliffe Union of Students (RUS)","Real Tennis","Recreational Experience and Arts Creativity with Harvard (REACH)","Red Cross","Republican Club","Reserve Officer Training Corps Association (HROTCA)","Response","Review of Environment and Society","Right to Life","River Charles Ensemble","Robotics Club","Romanian Association","Room 13","Rootstrikers","Running","Rural Health Association","Russian Speakers Association","Satire V","Scholars at Risk","School of Rock","Science Club for Girls","Science Fiction Association (HRSFA)","Science Review","Scientista","Scuba","Senior Class Committee","Seventh-day Adventist Fellowship (HCSDAF)","Sexual Health and Relationship Counselors (SHARC)","Sexual Health Education & Advocacy throughout Harvard College (SHEATH)","Shooting","Shotokan Karate","Sikh Student Association","Simplicissimus","Singaporean, Indonesia, and Malaysia Association (SIAMA)","Skiing","Social Enterprise Association (HCSEA)","Society for Mind, Brain, and Behavior (HSMBB)","Society for the Cinematic Arts","Society of Arab Students","Society of Black Scientists and Engineers (HSBSE)","Society of Physics Students (SPS)","SoulFood Christian Fellowship","South Asian Association (SAA)","South Asian Men's Collective (SAMC)","South Slavic Society","Speak Out Loud (SOL)","Special Olympics","Speedskating","Spikeball","Sports Analysis Collective","Sports Marketing Club","Springboard Design","Squash","Stand-Up Comic Society (HCSUCS)","Stories for Orphans","Story-Time Players","Student Astronomers at Harvard-Radcliffe (STAHR)","Student for Myanmar","Student Mental Health Liaisons (SMHL)","Students for Israel","Students for the Exploration and Development of Space (SEDS)","Swimming","Table Tennis","Taekwondo","Taiwan Leadership Conference","Taiwanese Cultural Society (TCS)","TAPS","Task Force on Asian and Pacific American Studies","Team HBV","TEATRO!","Tempus","Texas Club","Thai Society","The Advocate","The Happiness Project","The Harvard Callbacks","The Harvard Undergraduate Research Journal (THURJ)","The Ichthus","The Independent","The Review of Philosophy","Three Letter Acronym: Harold Team (TLA)","THUD (The Harvard Undergraduate Drummers)","Tough Mudder","Triathlon","Tuesday Magazine","Turkish Student Association","Ultimate Frisbee (Men)","Ultimate Frisbee (Women)","Under Construction","Undergraduate Council (UC)","Undergraduate Fellowship (HUF)","Undergraduate Research Association (HCURA)","United World Club","University Choir","US-India Initiative","Ventures (Harvard College)","Veritas Financial Group (VFG)","Veritones","Video Game Development Club","Vietnamese Association","VISION","Voice Actors' Guild","Volleyball (Men)","Volleyball (Women)","Water Polo","Wind Ensemble","Wine Society","Wireless Club","Wisconsin Club (H-COW)","Women in Business (HUWIB)","Women in Computer Science","Women's Basketball","Women's Ice Hockey","Women's Lacrosse","Women's Leadership Project (WLP)","Women's Soccer","Women's Tennis","Woodbridge International Society","World Model United Nations (WorldMUN)","Writers' Workshop","Writing and Public Service Initiative","Wushu","XFit","Yearbook","Youth Recreation Program- HOOPs","Asian American Christian Fellowship (AACF)","Korean Association (KA)","Korean International Student Association (KISA)","Korean Association (KA) Korean International Student Association (KISA)","Latinas Unidas","Native Americans at Harvard College (NAHC)","Nigerian Students Association (NSA)","Organization of Asian American Sisters in Service","Queer Students and Allies (QSA)","SHADE","Social Innovation Collaborative","South Asian Women's Collective","South Asian Dance Company","TEDx Harvard College","Philippine Forum","Hellenic Society"]
# A list of revenue types
revenues = ['Advertising', 'Contributions', 'Dues', 'Financial Gift', 'Fundraising', 'Merchandise Sale', 'Organizational Assets', 'Tickets/Participant Fees', 'Other']
# A list of expense types
expenses = ['Accommodations/Hotel', 'Admission Costs', 'Athletic Equipment', 'Competition Fees', 'Custodians', 'Decorations', 'Food', 'Licenses', 'Materials and Supplies', 'Personnel Fees', 'Photocopying/Printing', 'Photography', 'Posters', 'Production: Audio/Visual', 'Production: Costumes', 'Production: Instruments', 'Production: Lighting', 'Production: Music/Script/Rights', 'Production: Props', 'Production: Set', 'Production: Tech Equipment', 'Programs', 'Publicity', 'Salaries', 'Security/Police Detail', 'Space/Venue Rental', 'Travel/Transportation', 'Other']
# Random words used for generating random sentences
s_nouns = ["A dude", "My mom", "The king", "Some guy", "A cat with rabies", "A sloth", "Your homie", "This cool guy my gardener met yesterday", "Superman"]
s_verbs = ["eats", "kicks", "gives", "treats", "meets with", "creates", "hacks", "configures", "spies on", "retards", "meows on", "flees from", "tries to automate", "explodes"]
# Random list of names
names = ["Emma","Olivia","Sophia","Ava","Isabella","Mia","Abigail","Emily","Charlotte","Harper","Noah","Liam","Mason","Jacob","William","Ethan","James","Alexander","Michael","Benjamin"]

def rand_dollar(max_amt=1200.00):
    """ Generates a random float in [1.0,1200.00) with 2 decimal places """
    return str(round(uniform(1.0,max_amt), 2))
    
def rand_bool():
    """ Generates a random true or false """
    return choice([True, False])
    
def rand_club():
    """ Generates a random club """
    return choice(clubs)
    
def rand_sentence():
    """ Generates a random sentence """
    return choice(s_nouns) + " " + choice(s_verbs) + " " + choice(s_nouns).lower() + "."
    
def rand_word():
    """ Generates a random word """
    return choice(s_nouns)

def rand_phrase():
    """ Generates a random phrase """
    return choice(s_nouns) + " " + choice(s_verbs)
    
def rand_name():
    """ Generates a random name """
    return choice(names)
    
def rand_phone():
    """ Generates a random phone number """
    return str(randrange(100,1000)) + "-" + str(randrange(100,1000)) + "-" + str(randrange(1000,10000))

def rand_date():
    """ Generates a random date """
    return str(randrange(1,13)) + "/" + str(randrange(1,29)) + "/2017"
    
def rand_revenue():
    """ Generates a random type of revenue """
    return choice(revenues)
    
def rand_expense(small_grant=False):
    """ Generates a random type of expense """
    if small_grant:
        return choice(['Food','Publicity'])
    else:
        return choice(expenses)

def request_new_grant(domain, email, small_grant):
    """ Makes a GET request to create a new grant on the target domain """
    if small_grant:
        amount_requested = rand_dollar(200.00)
    else:
        amount_requested = rand_dollar()
    is_collaboration = choice(['Yes','No'])
    collaborators = ""
    collaboration_explanation = ""
    if is_collaboration:
        collaborators = rand_club()
        if rand_bool():
            collaborators += ", " + rand_club()
        collaboration_explanation = rand_sentence()
    contact_first_name = rand_name()
    contact_last_name = rand_name()
    contact_email = email
    contact_phone = rand_phone()
    contact_role = rand_word()
    is_upfront = str(randrange(1,3))
    organization = rand_club()
    tax_id = ""
    if rand_bool():
        tax_id = str(randrange(1000,10000))
    project = rand_phrase()
    project_description = rand_sentence() + " " + rand_sentence()
    is_event = choice(['Event', 'Something Else'])
    project_location = rand_word()
    project_start = rand_date()
    projet_end = rand_date()
    college_attendees = str(randrange(1,200))
    facebook_link = "facebook.com/" + rand_word()
    # Set all revenue default values to empty string
    revenue2_type=revenue2_description=revenue2_amount=revenue3_type=revenue3_description=revenue3_amount=revenue4_type=revenue4_description=revenue4_amount=revenue5_type=revenue5_description=revenue5_amount=revenue6_type=revenue6_description=revenue6_amount=revenue7_type=revenue7_description=revenue7_amount=revenue8_type=revenue8_description=revenue8_amount=revenue9_type=revenue9_description=revenue9_amount=revenue10_type=revenue10_description=revenue10_amount = ""
    revenue1_type = rand_revenue()
    revenue1_description = rand_sentence()
    revenue1_amount = rand_dollar()
    if rand_bool():
        revenue2_type = rand_revenue()
        revenue2_description = rand_sentence()
        revenue2_amount = rand_dollar()
        if rand_bool():
            revenue3_type = rand_revenue()
            revenue3_description = rand_sentence()
            revenue3_amount = rand_dollar()
            if rand_bool():
                revenue4_type = rand_revenue()
                revenue4_description = rand_sentence()
                revenue4_amount = rand_dollar()
                if rand_bool():
                    revenue5_type = rand_revenue()
                    revenue5_description = rand_sentence()
                    revenue5_amount = rand_dollar()
                    if rand_bool():
                        revenue6_type = rand_revenue()
                        revenue6_description = rand_sentence()
                        revenue6_amount = rand_dollar()
                        if rand_bool():
                            revenue7_type = rand_revenue()
                            revenue7_description = rand_sentence()
                            revenue7_amount = rand_dollar()
                            if rand_bool():
                                revenue8_type = rand_revenue()
                                revenue8_description = rand_sentence()
                                revenue8_amount = rand_dollar()
                                if rand_bool():
                                    revenue9_type = rand_revenue()
                                    revenue9_description = rand_sentence()
                                    revenue9_amount = rand_dollar()
                                    if rand_bool():
                                        revenue10_type = rand_revenue()
                                        revenue10_description = rand_sentence()
                                        revenue10_amount = rand_dollar()
    # Set all expense default values to empty string
    app_expense2_type=app_expense2_description=app_expense2_amount=app_expense3_type=app_expense3_description=app_expense3_amount=app_expense4_type=app_expense4_description=app_expense4_amount=app_expense5_type=app_expense5_description=app_expense5_amount=app_expense6_type=app_expense6_description=app_expense6_amount=app_expense7_type=app_expense7_description=app_expense7_amount=app_expense8_type=app_expense8_description=app_expense8_amount=app_expense9_type=app_expense9_description=app_expense9_amount=app_expense10_type=app_expense10_description=app_expense10_amount=app_expense11_type=app_expense11_description=app_expense11_amount=app_expense12_type=app_expense12_description=app_expense12_amount = ""
    if small_grant:
        app_expense1_type = rand_expense(True)
        app_expense1_description = rand_sentence()
        app_expense1_amount = rand_dollar(100.00)
        if rand_bool():
            app_expense2_type = rand_expense(True)
            app_expense2_description = rand_sentence()
            app_expense2_amount = rand_dollar(100.00)
    else:
        app_expense1_type = rand_expense()
        app_expense1_description = rand_sentence()
        app_expense1_amount = rand_dollar()
        if rand_bool():
            app_expense2_type = rand_expense()
            app_expense2_description = rand_sentence()
            app_expense2_amount = rand_dollar()
            if rand_bool():
                app_expense3_type = rand_expense()
                app_expense3_description = rand_sentence()
                app_expense3_amount = rand_dollar()
                if rand_bool():
                    app_expense4_type = rand_expense()
                    app_expense4_description = rand_sentence()
                    app_expense4_amount = rand_dollar()
                    if rand_bool():
                        app_expense5_type = rand_expense()
                        app_expense5_description = rand_sentence()
                        app_expense5_amount = rand_dollar()
                        if rand_bool():
                            app_expense6_type = rand_expense()
                            app_expense6_description = rand_sentence()
                            app_expense6_amount = rand_dollar()
                            if rand_bool():
                                app_expense7_type = rand_expense()
                                app_expense7_description = rand_sentence()
                                app_expense7_amount = rand_dollar()
                                if rand_bool():
                                    app_expense8_type = rand_expense()
                                    app_expense8_description = rand_sentence()
                                    app_expense8_amount = rand_dollar()
                                    if rand_bool():
                                        app_expense9_type = rand_expense()
                                        app_expense9_description = rand_sentence()
                                        app_expense9_amount = rand_dollar()
                                        if rand_bool():
                                            app_expense10_type = rand_expense()
                                            app_expense10_description = rand_sentence()
                                            app_expense10_amount = rand_dollar()
                                            if rand_bool():
                                                app_expense11_type = rand_expense()
                                                app_expense11_description = rand_sentence()
                                                app_expense11_amount = rand_dollar()
                                                if rand_bool():
                                                    app_expense12_type = rand_expense()
                                                    app_expense12_description = rand_sentence()
                                                    app_expense12_amount = rand_dollar()
    application_comments = rand_sentence()
    
    # Create Query String
    query_string = "amount_requested=" + amount_requested + "&"
    query_string += "is_collaboration=" + is_collaboration + "&"
    query_string += "collaborators=" + collaborators + "&"
    query_string += "collaboration_explanation=" + collaboration_explanation + "&"
    query_string += "contact_first_name=" + contact_first_name + "&"
    query_string += "contact_last_name=" + contact_last_name + "&"
    query_string += "contact_email=" + contact_email + "&"
    query_string += "contact_phone=" + contact_phone + "&"
    query_string += "contact_role=" + contact_role + "&"
    query_string += "is_upfront=" + is_upfront + "&"
    query_string += "organization=" + organization + "&"
    query_string += "tax_id=" + tax_id + "&"
    query_string += "project=" + project + "&"
    query_string += "project_description=" + project_description + "&"
    query_string += "is_event=" + is_event + "&"
    query_string += "project_location=" + project_location + "&"
    query_string += "project_start=" + project_start + "&"
    query_string += "project_end=" + projet_end + "&"
    query_string += "college_attendees=" + college_attendees + "&"
    query_string += "facebook_link=" + facebook_link + "&"
    query_string += "revenue1_type=" + revenue1_type + "&"
    query_string += "revenue1_description=" + revenue1_description + "&"
    query_string += "revenue1_amount=" + revenue1_amount + "&"
    query_string += "revenue2_type=" + revenue2_type + "&"
    query_string += "revenue2_description=" + revenue2_description + "&"
    query_string += "revenue2_amount=" + revenue2_amount + "&"
    query_string += "revenue3_type=" + revenue3_type + "&"
    query_string += "revenue3_description=" + revenue3_description + "&"
    query_string += "revenue3_amount=" + revenue3_amount + "&"
    query_string += "revenue4_type=" + revenue4_type + "&"
    query_string += "revenue4_description=" + revenue4_description + "&"
    query_string += "revenue4_amount=" + revenue4_amount + "&"
    query_string += "revenue5_type=" + revenue5_type + "&"
    query_string += "revenue5_description=" + revenue5_description + "&"
    query_string += "revenue5_amount=" + revenue5_amount + "&"
    query_string += "revenue6_type=" + revenue6_type + "&"
    query_string += "revenue6_description=" + revenue6_description + "&"
    query_string += "revenue6_amount=" + revenue6_amount + "&"
    query_string += "revenue7_type=" + revenue7_type + "&"
    query_string += "revenue7_description=" + revenue7_description + "&"
    query_string += "revenue7_amount=" + revenue7_amount + "&"
    query_string += "revenue8_type=" + revenue8_type + "&"
    query_string += "revenue8_description=" + revenue8_description + "&"
    query_string += "revenue8_amount=" + revenue8_amount + "&"
    query_string += "revenue9_type=" + revenue9_type + "&"
    query_string += "revenue9_description=" + revenue9_description + "&"
    query_string += "revenue9_amount=" + revenue9_amount + "&"
    query_string += "revenue10_type=" + revenue10_type + "&"
    query_string += "revenue10_description=" + revenue10_description + "&"
    query_string += "revenue10_amount=" + revenue10_amount + "&"
    query_string += "revenue10_type=" + revenue10_type + "&"
    query_string += "revenue10_description=" + revenue10_description + "&"
    query_string += "revenue10_amount=" + revenue10_amount + "&"
    query_string += "app_expense1_type=" + app_expense1_type + "&"
    query_string += "app_expense1_description=" + app_expense1_description + "&"
    query_string += "app_expense1_amount=" + app_expense1_amount + "&"
    query_string += "app_expense2_type=" + app_expense2_type + "&"
    query_string += "app_expense2_description=" + app_expense2_description + "&"
    query_string += "app_expense2_amount=" + app_expense2_amount + "&"
    query_string += "app_expense3_type=" + app_expense3_type + "&"
    query_string += "app_expense3_description=" + app_expense3_description + "&"
    query_string += "app_expense3_amount=" + app_expense3_amount + "&"
    query_string += "app_expense4_type=" + app_expense4_type + "&"
    query_string += "app_expense4_description=" + app_expense4_description + "&"
    query_string += "app_expense4_amount=" + app_expense4_amount + "&"
    query_string += "app_expense5_type=" + app_expense5_type + "&"
    query_string += "app_expense5_description=" + app_expense5_description + "&"
    query_string += "app_expense5_amount=" + app_expense5_amount + "&"
    query_string += "app_expense6_type=" + app_expense6_type + "&"
    query_string += "app_expense6_description=" + app_expense6_description + "&"
    query_string += "app_expense6_amount=" + app_expense6_amount + "&"
    query_string += "app_expense7_type=" + app_expense7_type + "&"
    query_string += "app_expense7_description=" + app_expense7_description + "&"
    query_string += "app_expense7_amount=" + app_expense7_amount + "&"
    query_string += "app_expense8_type=" + app_expense8_type + "&"
    query_string += "app_expense8_description=" + app_expense8_description + "&"
    query_string += "app_expense8_amount=" + app_expense8_amount + "&"
    query_string += "app_expense9_type=" + app_expense9_type + "&"
    query_string += "app_expense9_description=" + app_expense9_description + "&"
    query_string += "app_expense9_amount=" + app_expense9_amount + "&"
    query_string += "app_expense10_type=" + app_expense10_type + "&"
    query_string += "app_expense10_description=" + app_expense10_description + "&"
    query_string += "app_expense10_amount=" + app_expense10_amount + "&"
    query_string += "app_expense10_type=" + app_expense10_type + "&"
    query_string += "app_expense10_description=" + app_expense10_description + "&"
    query_string += "app_expense10_amount=" + app_expense10_amount + "&"
    query_string += "app_expense11_type=" + app_expense11_type + "&"
    query_string += "app_expense11_description=" + app_expense11_description + "&"
    query_string += "app_expense11_amount=" + app_expense11_amount + "&"
    query_string += "app_expense12_type=" + app_expense12_type + "&"
    query_string += "app_expense12_description=" + app_expense12_description + "&"
    query_string += "app_expense12_amount=" + app_expense12_amount + "&"
    query_string += "application_comments=" + application_comments + "&"
    query_string += "k=ZmL1kNBW1i"
    
    url = domain + "/new_grant?" + quote(query_string, "&=")
    req = get(url)
    print('\"' + project + '\" --> ' + str(req.status_code) + ", " + req.text)
    if req.status_code != 200:
        exit("Fatal: Bad Request Response")
        
def main():
    # Prompt user for inputs
    domain = input("Domain: ").rstrip('/')
    num_grants = int(input("Number of Grants: "))
    email = input("Email address for applications: ")
    # Make the http requests
    for i in range(num_grants):
        request_new_grant(domain, email, rand_bool())
    
if __name__ == "__main__":
    main()