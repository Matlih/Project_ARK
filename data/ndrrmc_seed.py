# FILE: backend/data/ndrrmc_seed.py

NDRRMC_TRAINING_DATA = [
    # --- CYCLONE PROGRESSION & TIMELINES ---
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Heavy rains started mid-July from the monsoon. LPAs formed near Palawan and Batangas, turning into TD Butchoy and TD Carina.",
        "output": "SITUATIONAL OVERVIEW: Since 11 July 2024, the Southwest Monsoon brought moderate to heavy rains over different provinces in the country. On 19 July 2024, the Low Pressure Area over the West Philippine Sea west of Batangas developed into Tropical Depression (TD) 'BUTCHOY', while another LPA over the Philippine Sea developed into Tropical Depression (TD) 'CARINA'."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Carina enhanced the monsoon and dumped rain on western Luzon. Butchoy left PAR. Carina kept getting stronger over the Philippine Sea until it became a Typhoon.",
        "output": "SITUATIONAL OVERVIEW: The Southwest Monsoon, enhanced alongside TD 'CARINA', brought moderate to heavy rains over the western portion of Luzon. While TD 'BUTCHOY' exited the Philippine Area of Responsibility (PAR) on 20 July 2024, 'CARINA' steadily intensified as it moved northwestward over the Philippine Sea, strengthening to Typhoon category by 22 July 2024."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Carina became a Super Typhoon near Taiwan. Batanes and Cagayan got signal number 1 and 2 warnings.",
        "output": "SITUATIONAL OVERVIEW: On 24 July 2024, 'CARINA' intensified into a Super Typhoon as it headed towards Taiwan. Tropical Cyclone Wind Signal (TCWS) No. 2 was hoisted in Batanes, while TCWS No. 1 was hoisted over the Babuyan Islands, the northern portion of mainland Cagayan, and the northern portion of Ilocos Norte."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Carina crossed Taiwan, weakened, and left PAR heading to China. The monsoon weakened but still brought rain to Ilocos and Batanes.",
        "output": "SITUATIONAL OVERVIEW: On 25 July 2024, 'CARINA' crossed Taiwan, further weakened, and exited the Philippine Area of Responsibility (PAR) towards southeastern China. By 26 July 2024, the enhanced Southwest Monsoon began to weaken, though it continued to bring scattered rainshowers and thunderstorms over the Ilocos Region, Cordillera Administrative Region, Batanes, Babuyan Islands, Zambales, and Bataan."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Typhoon Aghon entered PAR. Eastern Samar under Signal No 1.",
        "output": "SITUATIONAL OVERVIEW: At 08:00 AM today, Tropical Cyclone 'AGHON' officially entered the Philippine Area of Responsibility (PAR). Consequently, Tropical Cyclone Wind Signal (TCWS) No. 1 has been hoisted over the province of Eastern Samar."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Typhoon Bising left PAR at 5 AM. Rains still hitting Bicol.",
        "output": "SITUATIONAL OVERVIEW: As of 5:00 AM, Typhoon 'BISING' has exited the Philippine Area of Responsibility (PAR). However, the trough of the cyclone continues to bring light to moderate rainshowers over the Bicol Region."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Storm over Mindanao made landfall in Surigao.",
        "output": "SITUATIONAL OVERVIEW: At approximately 02:00 PM, the center of the Tropical Storm made its initial landfall in the vicinity of Surigao City, Surigao del Norte, bringing torrential rains and gale-force winds."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "LPA turned into a tropical depression east of Visayas.",
        "output": "SITUATIONAL OVERVIEW: The Low Pressure Area (LPA) previously monitored east of the Visayas has developed into a Tropical Depression. State weather bureau PAGASA continues to monitor its trajectory."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Monsoon enhanced by typhoon causing floods in Metro Manila.",
        "output": "SITUATIONAL OVERVIEW: The continuous enhancement of the Southwest Monsoon (Habagat) by the active Tropical Cyclone has precipitated widespread urban flooding across low-lying areas in Metro Manila."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Typhoon weakened into an LPA after hitting Sierra Madre.",
        "output": "SITUATIONAL OVERVIEW: Upon traversing the Sierra Madre mountain range, the severe tropical storm has rapidly degraded and weakened into a remnant Low Pressure Area (LPA)."
    },

    # --- AFFECTED POPULATIONS & ECs ---
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Over 6.4 million people (1.7 million families) were affected. About 4.5k families are in 94 evacuation centers, and over 250k families are getting help outside.",
        "output": "AFFECTED POPULATION: A total of 1,734,099 families or 6,498,918 persons were affected. Of which, 4,510 families or 18,517 persons were served inside 94 Evacuation Centers (ECs) and 253,936 families or 1,123,409 persons were served outside ECs."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "12,000 families affected in Region 3. 500 in evacuation centers.",
        "output": "AFFECTED POPULATION: A total of 12,000 families or approximately 48,000 persons were affected in Region III. Currently, 500 families are taking temporary shelter in pre-identified Evacuation Centers (ECs)."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Preemptive evacuation in coastal towns. 300 families moved.",
        "output": "ACTIONS TAKEN: Local Government Units (LGUs) have initiated forced and preemptive evacuation protocols in high-risk coastal municipalities. A total of 300 families have been successfully relocated to designated Evacuation Centers (ECs)."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "50,000 people displaced in Mindanao floods. 120 camps open.",
        "output": "AFFECTED POPULATION: Pervasive flooding in Mindanao has displaced approximately 50,000 individuals. To accommodate the Internally Displaced Persons (IDPs), 120 Evacuation Centers (ECs) remain actively managed by the DSWD."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Evacuation centers closed. People went home.",
        "output": "STATUS OF ECs: Following the cessation of the severe weather event, all previously activated Evacuation Centers (ECs) have been officially decamped. The affected populace has safely returned to their respective residences."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "1 million people affected nationwide. 50k inside shelters, 200k getting food outside.",
        "output": "AFFECTED POPULATION: National consolidations indicate 1,000,000 persons affected across all regions. Of this figure, 50,000 individuals are served inside active Evacuation Centers (ECs), while 200,000 individuals are provided with relief assistance outside ECs."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "No evacuations needed in Ilocos despite rain.",
        "output": "AFFECTED POPULATION: Despite the recorded precipitation, no preemptive evacuations were deemed necessary in the Ilocos Region. Zero Internally Displaced Persons (IDPs) have been reported."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Camps are full. Need more space for 500 families.",
        "output": "STATUS OF ECs: Operational Evacuation Centers (ECs) in the affected municipalities have reached maximum capacity. The Camp Coordination and Camp Management (CCCM) cluster is identifying modular facilities to accommodate an overflow of 500 families."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "DSWD provided food packs to 10,000 affected families.",
        "output": "RELIEF OPERATIONS: The Department of Social Welfare and Development (DSWD) has successfully distributed Family Food Packs (FFPs) and non-food items to 10,000 affected families residing both inside and outside Evacuation Centers (ECs)."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "LGUs managing 45 active evacuation centers in the province.",
        "output": "STATUS OF ECs: Provincial Disaster Risk Reduction and Management Offices (PDRRMOs) report the active maintenance and continuous provisioning of 45 Evacuation Centers (ECs) across the province."
    },

    # --- CASUALTIES & INJURIES ---
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "48 people died, 16 got hurt, and 5 are missing.",
        "output": "CASUALTIES: A total of 48 dead, 16 injured, and 5 missing persons were reported. The Management of the Dead and Missing (MDM) cluster is continuously validating these figures with local authorities."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "2 dead from landslide, 1 injured.",
        "output": "CASUALTIES: Initial reports indicate 2 fatalities and 1 injured individual resulting from a rain-induced landslide. Subject to validation by the Management of the Dead and Missing (MDM) cluster."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "No casualties reported so far.",
        "output": "CASUALTIES: As of this reporting period, there are zero (0) reported casualties, injuries, or missing persons associated with the weather disturbance."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "10 fishermen missing off coast of Samar.",
        "output": "CASUALTIES: A total of 10 maritime personnel (fisherfolk) are currently reported missing off the coast of Samar following gale-force winds. Search and Rescue (SAR) operations by the Philippine Coast Guard are ongoing."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "15 injured by flying debris during the typhoon.",
        "output": "CASUALTIES: Health clusters report 15 individuals sustaining minor to moderate injuries due to flying debris. All injured persons have been provided immediate medical attention at local Rural Health Units (RHUs)."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Number of dead went up to 100 after floods.",
        "output": "CASUALTIES: The Management of the Dead and Missing (MDM) cluster has verified an escalation in fatalities, confirming a total of 100 dead due to severe inundation. Validation processes remain active."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "3 people died from electrocution.",
        "output": "CASUALTIES: Three (3) fatalities were recorded secondary to electrocution incidents during the height of the flooding. The Department of the Interior and Local Government (DILG) is securing the incident reports."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Casualties are being verified by DILG.",
        "output": "CASUALTIES: Reports of casualties from regional counterparts have been received. However, these figures are currently undergoing strict validation by the DILG Management of the Dead and Missing (MDM) cluster before official inclusion in the national registry."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "1 rescuer injured during operations.",
        "output": "CASUALTIES: One (1) responder sustained injuries during the conduct of Search, Rescue, and Retrieval (SRR) operations. The individual is currently in stable condition."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "A massive amount of people were hit by the storm. 6,498,918 people total. 48 are confirmed dead, and 94 evacuation centers are currently active holding 18,517 people.",
        "output": "SITUATIONAL OVERVIEW: The National Disaster Risk Reduction and Management Council (NDRRMC) reports significant impacts on the civilian populace.\n\nAFFECTED POPULATION: A total of 1,734,099 families or 6,498,918 persons were affected. Currently, 4,510 families or 18,517 persons are taking temporary shelter in 94 Evacuation Centers (ECs).\n\nCASUALTIES: A total of 48 dead, 16 injured, and 5 missing persons were reported."
    },

    # --- INFRASTRUCTURE, AGRI DAMAGE & LIFELINES ---
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Damage to rice and corn is 500 million pesos.",
        "output": "COST OF DAMAGE TO AGRICULTURE: The Department of Agriculture (DA) reports an estimated PHP 500,000,000.00 in agricultural damages, primarily affecting high-value rice and corn crops across the region."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "3 bridges collapsed, costing 200 million pesos to fix.",
        "output": "COST OF DAMAGE TO INFRASTRUCTURE: Initial assessments from the Department of Public Works and Highways (DPWH) indicate the total collapse of 3 major bridge structures, with an estimated rehabilitation cost of PHP 200,000,000.00."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Power is out in 15 cities.",
        "output": "STATUS OF LIFELINES (POWER): A total of 15 cities and municipalities are currently experiencing total power interruption. Restoration efforts by local electric cooperatives and the National Grid Corporation of the Philippines (NGCP) are ongoing."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Flights cancelled at NAIA due to weather.",
        "output": "STATUS OF LIFELINES (TRANSPORTATION): The Manila International Airport Authority (MIAA) has reported the cancellation of multiple domestic and international flights at the Ninoy Aquino International Airport (NAIA) due to unfavorable meteorological conditions."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Roads blocked by landslides in Benguet.",
        "output": "STATUS OF LIFELINES (ROADS): Several national and arterial road networks in the province of Benguet are currently impassable to all types of vehicles due to rain-induced soil collapse and landslides. DPWH clearing operations are underway."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Water supply cut off in 5 barangays.",
        "output": "STATUS OF LIFELINES (WATER): Five (5) barangays are experiencing water supply interruptions following damage to primary pipelines. Local water districts have deployed mobile water tankers to mitigate the deficit."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Total damage is 1 billion pesos.",
        "output": "TOTAL COST OF DAMAGE: The consolidated initial assessment places the total economic impact—encompassing both agriculture and infrastructure—at an estimated PHP 1,000,000,000.00."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "No damage to infra reported yet.",
        "output": "COST OF DAMAGE TO INFRASTRUCTURE: As of the current reporting period, there are no structural damages reported by the DPWH. Continuous monitoring and ground validation are in effect."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Seaports suspended trips. Passengers stranded.",
        "output": "STATUS OF LIFELINES (MARITIME): The Philippine Coast Guard (PCG) has strictly implemented a 'No Sail Policy.' All maritime vessel trips are suspended, resulting in stranded passengers, rolling cargoes, and vessels across affected seaports."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Cell signal is down in the province.",
        "output": "STATUS OF LIFELINES (COMMUNICATIONS): Significant telecommunications outages have been reported across the province. The Department of Information and Communications Technology (DICT) is coordinating with major telco providers for immediate network restoration."
    },

    # --- DECLARATIONS & ASSISTANCE ---
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Province declared State of Calamity.",
        "output": "DECLARATION OF STATE OF CALAMITY: The Sangguniang Panlalawigan has officially passed a resolution declaring the entire province under a State of Calamity, authorizing the utilization of the local Quick Response Fund (QRF)."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Government gave 5 million pesos in aid.",
        "output": "COST OF ASSISTANCE: A total of PHP 5,000,000.00 worth of humanitarian assistance has been provided to the affected populations by the DSWD, LGUs, and Non-Government Organizations (NGOs)."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "National government sending C130 with relief goods.",
        "output": "ACTIONS TAKEN: The National Disaster Risk Reduction and Management Council (NDRRMC) has mobilized the Armed Forces of the Philippines (AFP) to deploy C-130 aircraft for the immediate logistical transport of Family Food Packs (FFPs) to isolated areas."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Classes suspended in all levels.",
        "output": "SUSPENSION OF CLASSES AND WORK: Local Chief Executives (LCEs) across affected regions have issued memorandums declaring the suspension of classes at all levels (public and private) and the suspension of work in government offices."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Asking for international help.",
        "output": "ACTIONS TAKEN: Given the magnitude of the disaster, the National Government is coordinating with the international humanitarian community and foreign embassies for potential augmentation of response and recovery resources."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Red alert raised at NDRRMC.",
        "output": "EMERGENCY PREPAREDNESS: The NDRRMC Operations Center has elevated its alert status to RED. All member agencies and Regional DRRMCs are directed to activate their respective Emergency Operations Centers (EOCs) to the highest level."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Providing psychosocial support to victims.",
        "output": "ACTIONS TAKEN: The Department of Health (DOH), in coordination with the DSWD, has deployed personnel to conduct Mental Health and Psychosocial Support (MHPSS) interventions for Internally Displaced Persons (IDPs) inside ECs."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Police deployed to prevent looting.",
        "output": "ACTIONS TAKEN: The Philippine National Police (PNP) has deployed additional personnel to heavily affected commercial districts and evacuated residential areas to maintain peace and order and deter potential looting incidents."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Price freeze on basic goods implemented.",
        "output": "ACTIONS TAKEN: Following the declaration of a State of Calamity, the Department of Trade and Industry (DTI) has strictly implemented a 60-day price freeze on basic necessities and prime commodities to protect consumers."
    },
    {
        "instruction": "Generate formal NDRRMC situation report based on this summary:",
        "input": "Total damage 15B, 100 dead, state of calamity declared.",
        "output": "SITUATIONAL OVERVIEW: The catastrophic weather event has resulted in an estimated PHP 15,000,000,000.00 in combined economic losses.\n\nCASUALTIES: The MDM cluster has verified 100 fatalities.\n\nDECLARATION: A nationwide State of Calamity has been declared to expedite rescue, relief, and rehabilitation efforts."
    }
]