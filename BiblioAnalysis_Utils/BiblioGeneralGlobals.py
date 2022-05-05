__all__ = ['ALIAS_UK',
           'BOLD_TEXT',
           'CHANGE',
           'COUNTRIES',
           'COUNTRIES_GPS',
           'DIC_CHANGE_CHAR',
           'IN_TO_MM',
           'LIGHT_TEXT',
           'USA_STATES',]

# Text format control
BOLD_TEXT = '\033[1m'
LIGHT_TEXT = '\033[0m'

# Countries normalized names and GPS coordinates
COUNTRY = '''
    United States,Afghanistan,Albania,Algeria,American Samoa,Andorra,Angola,
    Anguilla,Antarctica,Antigua And Barbuda,Argentina,Armenia,Aruba,Australia,
    Austria,Azerbaijan,Bahamas,Bahrain,Bangladesh,Barbados,Belarus,Belgium,
    Belize,Benin,Bermuda,Bhutan,Bolivia,Bosnia And Herzegowina,Botswana,Bouvet Island,
    Brazil,Brunei Darussalam,Bulgaria,Burkina Faso,Burundi,Cambodia,Cameroon,Canada,
    Cape Verde,Cayman Islands,Central African Rep,Chad,Chile,China,Christmas Island,
    Cocos Islands,Colombia,Comoros,Congo,Cook Islands,Costa Rica,Cote D`ivoire,Croatia,
    Cuba,Cyprus,Czech Republic,Denmark,Djibouti,Dominica,Dominican Republic,East Timor,
    Ecuador,Egypt,El Salvador,Equatorial Guinea,Eritrea,Estonia,Ethiopia,Falkland Islands (Malvinas),
    Faroe Islands,Fiji,Finland,France,French Guiana,French Polynesia,French S. Territories,
    Gabon,Gambia,Georgia,Germany,Ghana,Gibraltar,Greece,Greenland,Grenada,Guadeloupe,Guam,
    Guatemala,Guinea,Guinea-bissau,Guyana,Haiti,Honduras,Hong Kong,Hungary,Iceland,India,
    Indonesia,Iran,Iraq,Ireland,Israel,Italy,Jamaica,Japan,Jordan,Kazakhstan,Kenya,Kiribati,
    North Korea,South Korea,Kuwait,Kyrgyzstan,Laos,Latvia,Lebanon,Lesotho,Liberia,Libya,
    Liechtenstein,Lithuania,Luxembourg,Macau,Macedonia,Madagascar,Malawi,Malaysia,Maldives,
    Mali,Malta,Marshall Islands,Martinique,Mauritania,Mauritius,Mayotte,Mexico,Micronesia,
    Moldova,Monaco,Mongolia,Montserrat,Morocco,Mozambique,Myanmar,Namibia,Nauru,Nepal,Netherlands,
    Netherlands Antilles,New Caledonia,New Zealand,Nicaragua,Niger,Nigeria,Niue,Norfolk Island,
    Northern Mariana Islands,Norway,Oman,Pakistan,Palau,Panama,Papua New Guinea,Paraguay,Peru,
    Philippines,Pitcairn,Poland,Portugal,Puerto Rico,Qatar,Reunion,Romania,Russian Federation,
    Rwanda,Saint Kitts And Nevis,Saint Lucia,St Vincent/Grenadines,Samoa,San Marino,Sao Tome,
    Saudi Arabia,Senegal,Seychelles,Sierra Leone,Singapore,Slovakia,Slovenia,Solomon Islands,
    Somalia,South Africa,Spain,Sri Lanka,St. Helena,St.Pierre,Sudan,Suriname,Swaziland,Sweden,
    Switzerland,Syrian Arab Republic,Taiwan,Tajikistan,Tanzania,Thailand,Togo,Tokelau,Tonga,
    Trinidad And Tobago,Tunisia,Turkey,Turkmenistan,Tuvalu,Uganda,Ukraine,United Arab Emirates,
    United Kingdom,Uruguay,Uzbekistan,Vanuatu,Vatican City State,Venezuela,Viet Nam,Virgin Islands (British),
    Virgin Islands (U.S.),Western Sahara,Yemen,Yugoslavia,Zaire,Zambia,Zimbabwe
'''
COUNTRIES = [x.strip() for x in COUNTRY.split(',')]

USA_STATES = '''AL,AK,AZ,AR,CA,CO,CT,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,
NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY'''
USA_STATES = [x.strip() for x in USA_STATES.split(',')]

ALIAS_UK = '''England,Wales,North Ireland,Scotland'''
ALIAS_UK = [x.strip() for x in ALIAS_UK.split(',')] 

COUNTRIES_GPS_STRING = '''Aruba:12.5,-69.97;Afghanistan:33,65;Angola:-12.5,18.5;Anguilla:18.25,-63.17;
Albania:41,20;Andorra:42.5,1.5;United Arab Emirates:24,54;Argentina:-34,-64;Armenia:40,45;
American Samoa:-14.33,-170;Antarctica:-90,0;French Southern and Antarctic Lands:-49.25,69.167;
Antigua And Barbuda:17.05,-61.8;Australia:-27,133;Austria:47.3,13.3;Azerbaijan:40.5,47.5;
Burundi:-3.5,30;Belgium:50.83,4;Benin:9.5,2.25;Burkina Faso:13,-2;Bangladesh:24,90;Bulgaria:43,25;
Bahrain:26,50.55;Bahamas:24.25,-76;Bosnia And Herzegowina:44,18;Saint Barthélemy:18.5,-63.417;
Belarus:53,28;Belize:17.25,-88.75;Bermuda:32.3,-64.75;Bolivia:-17,-65;Brazil:-10,-55;
Barbados:13.16,-59.53;Brunei Darussalam:4.5,114.67;Bhutan:27.5,90.5;Bouvet Island:-54.43,3.4;
Botswana:-22,24;Central African Rep:7,21;Canada:60,-95;Switzerland:47,8;Chile:-30,-71;China:35,105;
IvoryCoast:8,-5;Cameroon:6,12;Congo:0,25;Republic of theCongo:-1,15;Cook Islands:-21.23,-159.77;
Colombia:4,-72;Comoros:-12.17,44.25;Cape Verde:16,-24;Costa Rica:10,-84;Cuba:21.5,-80;
Curacao:12.116667,-68.933333;Christmas Island:-10.5,105.66;Cayman Islands:19.5,-80.5;Cyprus:35,33;
Czech Republic:49.75,15.5;Germany:51,9;Djibouti:11.5,43;Dominica:15.416,-61.33;Denmark:56,10;
Dominican Republic:19,-70.7;Algeria:28,3;Ecuador:-2,-77.5;Egypt:27,30;Eritrea:15,39;Western Sahara:24.5,-13;
Spain:40,-4;Estonia:59,26;Ethiopia:8,38;Finland:64,26;Fiji:-18,175;Falkland Islands:-51.75,-59;
France:46,2;Faroe Islands:62,-7;Micronesia:6.917,158.25;Gabon:-1,11.75;United Kingdom:54,-2;
Georgia:42,43.5;Guernsey:49.46,-2.583;Ghana:8,-2;Gibraltar:36.13,-5.35;Guinea:11,-10;
Guadeloupe:16.25,-61.583;Gambia:13.47,-16.57;Guinea-bissau:12,-15;Equatorial Guinea:2,10;Greece:39,22;
Grenada:12.117,-61.67;Greenland:72,-40;Guatemala:15.5,-90.25;French Guiana:4,-53;Guam:13.47,144.783;
Guyana:5,-59;Hong Kong:22.267,114.188;Honduras:15,-86.5;Croatia:45.17,15.5;Haiti:19,-72.417;Hungary:47,20;
Indonesia:-5,120;Isle of Man:54.25,-4.5;India:20,77;British Indian Ocean Territory:-6,71.5;Ireland:53,-8;
Iran:32,53;Iraq:33,44;Iceland:65,-18;Israel:31.47,35.13;Italy:42.83,12.83;Jamaica:18.25,-77.5;
Jersey:49.25,-2.17;Jordan:31,36;Japan:36,138;Kazakhstan:48,68;Kenya:1,38;Kyrgyzstan:41,75;Cambodia:13,105;
Kiribati:1.417,173;Saint Kitts And Nevis:17.33,-62.75;South Korea:37,127.5;Kosovo:42.67,21.17;Kuwait:29.5,45.75;
Laos:18,105;Lebanon:33.83,35.83;Liberia:6.5,-9.5;Libya:25,17;Saint Lucia:13.883,-60.97;Liechtenstein:47.27,9.53;
Sri Lanka:7,81;Lesotho:-29.5,28.5;Lithuania:56,24;Luxembourg:49.75,6.16;Latvia:57,25;Macau:22.17,113.55;
Saint Martin:18.083,-63.95;Morocco:32,-5;Monaco:43.73,7.4;Moldova:47,29;Madagascar:-20,47;Maldives:3.25,73;
Mexico:23,-102;Marshall Islands:9,168;Macedonia:41.83,22;Mali:17,-4;Malta:35.83,14.583;Myanmar:22,98;
Montenegro:42.5,19.3;Mongolia:46,105;Northern Mariana Islands:15.2,145.75;Mozambique:-18.25,35;Mauritania:20,-12;
Montserrat:16.75,-62.2;Martinique:14.67,-61;Mauritius:-20.283,57.55;Malawi:-13.5,34;Malaysia:2.5,112.5;
Mayotte:-12.83,45.17;Namibia:-22,17;New Caledonia:-21.5,165.5;Niger:16,8;Norfolk Island:-29.03,167.95;
Nigeria:10,8;Nicaragua:13,-85;Niue:-19.03,-169.87;Netherlands:52.5,5.75;Norway:62,10;Nepal:28,84;
Nauru:-0.53,166.917;New Zealand:-41,174;Oman:21,57;Pakistan:30,70;Panama:9,-80;Pitcairn:-25.07,-130.1;
Peru:-10,-76;Philippines:13,122;Palau:7.5,134.5;Papua New Guinea:-6,147;Poland:52,20;Puerto Rico:18.25,-66.5;
North Korea:40,127;Portugal:39.5,-8;Paraguay:-23,-58;Palestine:31.9,35.2;French Polynesia:-15,-140;Qatar:25.5,51.25;
Reunion:-21.15,55.5;Romania:46,25;Russian Federation:60,100;Rwanda:-2,30;Saudi Arabia:25,45;Sudan:15,30;Senegal:14,-14;
Singapore:1.36,103.8;SouthGeorgia:-54.5,-37;Svalbard and Jan Mayen:78,20;Solomon Islands:-8,159;
Sierra Leone:8.5,-11.5;El Salvador:13.83,-88.916;San Marino:43.76,12.416;Somalia:10,49;
SaintPierreandMiquelon:46.83,-56.33;Serbia:44,21;SouthSudan:7,30;Sao Tome:1,7;
Suriname:4,-56;Slovakia:48.66,19.5;Slovenia:46.116,14.816;Sweden:62,15;Swaziland:-26.5,31.5;
Sint Maarten:18.03,-63.05;Seychelles:-4.583,55.66;Syrian Arab Republic:35,38;TurksandCaicosIslands:21.75,-71.583;
Chad:15,19;Togo:8,1.16;Thailand:15,100;Tajikistan:39,71;Tokelau:-9,-172;Turkmenistan:40,60;East Timor:-8.83,125.916;
Tonga:-20,-175;Trinidad And Tobago:11,-61;Tunisia:34,9;Turkey:39,35;Tuvalu:-8,178;Taiwan:23.5,121;Tanzania:-6,35;
Uganda:1,32;Ukraine:49,32;United States Minor Outlying Islands:19.2911437,166.618332;Uruguay:-33,-56;United States:38,-97;
Uzbekistan:41,64;Vatican City State:41.9,12.45;St Vincent/Grenadines:13.25,-61.2;Venezuela:8,-66;
Virgin Islands (British):18.431383,-64.62305;Virgin Islands (U.S.):18.35,-64.933333;Viet Nam:16.16,107.83;
Vanuatu:-16,167;Wallis and Futuna:-13.3,-176.2;Samoa:-13.583,-172.33;Yemen:15,48;South Africa:-29,24;
Zambia:-15,30;Zimbabwe:-20,30'''

import re
pattern = re.compile(r"^[\n]{0,1}(?P<country>[\w\s\-\(\)\./]+):(?P<long>[\d\.\-]+),(?P<lat>[\d\.\-]+)$",re.M)

COUNTRIES_GPS = {}
for country in COUNTRIES_GPS_STRING.split(';'):
    match = pattern.search(country)
    COUNTRIES_GPS[match.group("country")] = (float(match.group("long")),float(match.group("lat")))

# Character replacements
DIC_CHANGE_CHAR = {"Ł":"L",   # polish capital to L 
                   "ł":"l",   # polish l
                   "ı":"i",    
                   "‐":"-",   # Non-Breaking Hyphen to hyphen-minus
                   "—":"-",   # En-dash to hyphen-minus
                   "–":"-",   # Em-dash to hyphen-minus
                   "Đ":"D",   # D with stroke (Vietamese,South Slavic) to D
                   ".":"",
                   ",":""}

CHANGE = str.maketrans(DIC_CHANGE_CHAR)

IN_TO_MM = 25.4