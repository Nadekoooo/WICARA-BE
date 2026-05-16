import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GRAPH_PATH = ROOT / "backend" / "app" / "modules" / "curriculum" / "data" / "wicara_kurikulum_merdeka_graph_complete.json"
SEED_DIR = ROOT / "backend" / "bank_soal" / "seeds"


SUBJECT_GROUPS = {
    "ipas": {
        "education_level": "elementary",
        "grade_band": "elementary",
        "phases": {"A", "B", "C"},
        "level_short": "el",
        "subject_short": "ipas",
        "filename_subject": "ipas",
    },
    "ipa": {
        "education_level": "junior_high",
        "grade_band": "junior_high",
        "phases": {"D"},
        "level_short": "jh",
        "subject_short": "ipa",
        "filename_subject": "ipa",
    },
    "fisika": {
        "education_level": "senior_high",
        "grade_band": "senior_high",
        "phases": {"E", "F"},
        "level_short": "sh",
        "subject_short": "phy",
        "filename_subject": "fisika",
    },
    "kimia": {
        "education_level": "senior_high",
        "grade_band": "senior_high",
        "phases": {"E", "F"},
        "level_short": "sh",
        "subject_short": "chem",
        "filename_subject": "kimia",
    },
    "biologi": {
        "education_level": "senior_high",
        "grade_band": "senior_high",
        "phases": {"E", "F"},
        "level_short": "sh",
        "subject_short": "bio",
        "filename_subject": "biologi",
    },
}


ASSESSMENT_VARIANTS = {
    "pretest": {
        "short": "pre",
        "helper_text": "Choose the topic that best matches the key foundational idea.",
        "prompt_templates": [
            "Which topic best matches this prerequisite idea: {description}?",
            "Before studying this strand, which topic would assess {description}?",
            "Which topic should a learner know first for {description}?",
        ],
    },
    "daily_quiz": {
        "short": "daily",
        "helper_text": "Pick the topic that best matches the idea.",
        "prompt_templates": [
            "Which topic is about {description}?",
            "A quick review of {description} belongs to which topic?",
            "Which topic should be reviewed for {description}?",
        ],
    },
    "posttest": {
        "short": "post",
        "helper_text": "Choose the topic that best fits the full science idea.",
        "prompt_templates": [
            "After learning this strand, which topic best fits {description}?",
            "Which topic most directly applies to {description}?",
            "Which topic best represents this learned idea: {description}?",
        ],
    },
    "workspace_quiz": {
        "short": "work",
        "helper_text": "Pick the best topic match.",
        "prompt_templates": [
            "Topic for {description}?",
            "Which topic matches {description}?",
            "Which topic fits {description}?",
        ],
    },
}


PHRASE_OVERRIDES = {
    "keterampilan_observasi_dan_bertanya": "Observation and questioning skills",
    "anggota_tubuh_pancaindra_dan_kesehatan": "Body parts, senses, and health",
    "ciri_makhluk_hidup_dan_kebutuhannya": "Characteristics and needs of living things",
    "hewan_dan_tumbuhan_di_lingkungan_sekitar": "Animals and plants in the local environment",
    "benda_dan_sifat_sederhana": "Objects and simple properties",
    "perubahan_benda_sederhana": "Simple changes in materials",
    "gerak_benda_dorongan_dan_tarikan": "Motion from pushes and pulls",
    "cuaca_dan_musim_sehari_hari": "Everyday weather and seasons",
    "siang_malam_dan_benda_langit": "Day, night, and objects in the sky",
    "lingkungan_bersih_sampah_dan_kebiasaan_menjaga_alam": "Clean environments, waste, and caring for nature",
    "siklus_hidup_hewan_dan_tumbuhan": "Life cycles of animals and plants",
    "bagian_tubuh_manusia_dan_pancaindra": "Human body parts and the senses",
    "bagian_tumbuhan_dan_fungsinya": "Plant parts and their functions",
    "bentuk_permukaan_bumi_dan_sumber_daya_alam": "Earth's surface features and natural resources",
    "campuran_dan_pemisahan_sederhana": "Mixtures and simple separation methods",
    "daur_air_dan_cuaca": "The water cycle and weather",
    "energi_panas_cahaya_bunyi_listrik_sederhana": "Introductory heat, light, sound, and electricity",
    "gaya_gerak_gesek_dan_magnet_sederhana": "Introductory force, motion, friction, and magnets",
    "habitat_dan_adaptasi_awal": "Introductory habitats and adaptation",
    "keterampilan_investigasi_variabel_sederhana": "Investigation skills and simple variables",
    "pengelompokan_hewan_dan_tumbuhan": "Grouping animals and plants",
    "rantai_makanan_sederhana": "Simple food chains",
    "sumber_energi_dan_penghematan_energi": "Energy sources and saving energy",
    "wujud_zat_dan_perubahan_wujud": "States of matter and changes of state",
    "bumi_bulan_matahari_dan_tata_surya": "Earth, moon, sun, and the solar system",
    "cahaya_bunyi_dan_indra": "Light, sound, and the senses",
    "ekosistem_dan_interaksi_makhluk_hidup": "Ecosystems and interactions of living things",
    "fotosintesis_dan_aliran_energi_pada_makhluk_hidup": "Photosynthesis and energy flow in living things",
    "kalor_dan_perpindahan_panas": "Heat and heat transfer",
    "keseimbangan_ekosistem_dan_pelestarian": "Ecosystem balance and preservation",
    "listrik_dan_rangkaian_sederhana": "Electricity and simple circuits",
    "magnet_dan_penerapannya": "Magnets and their applications",
    "metode_ilmiah_data_tabel_dan_grafik_sederhana": "Scientific methods, tables, and simple graphs",
    "perubahan_fisika_dan_kimia_dasar": "Introductory physical and chemical changes",
    "pesawat_sederhana": "Simple machines",
    "pubertas_dan_kesehatan_tubuh_dasar": "Puberty and basic body health",
    "rotasi_revolusi_dan_musim": "Rotation, revolution, and seasons",
    "sistem_pencernaan_pernapasan_dan_peredaran_darah_awal": "Introductory digestive, respiratory, and circulatory systems",
    "sumber_daya_alam_dan_perubahan_lingkungan": "Natural resources and environmental change",
    "zat_campuran_larutan_dan_sifat_bahan": "Matter, mixtures, solutions, and material properties",
    "asam_basa_dasar_dalam_kehidupan": "Introductory acids and bases in daily life",
    "benda_dan_zat": "Objects and matter",
    "bioteknologi_dasar": "Introductory biotechnology",
    "fase_bulan": "Phases of the moon",
    "gangguan_pada_sistem_organ": "Disorders of organ systems",
    "gerak_bumi_bulan_matahari": "Motion of Earth, moon, and sun",
    "gerak_dan_gaya": "Motion and force",
    "gerhana": "Eclipses",
    "interaksi_makhluk_hidup_dan_lingkungan": "Interactions of living things and the environment",
    "keselamatan_penggunaan_bahan": "Safe use of materials",
    "keterkaitan_listrik_dan_magnet": "Relationships between electricity and magnetism",
    "litosfer_hidrosfer_atmosfer": "Lithosphere, hydrosphere, and atmosphere",
    "magnet_dan_kemagnetan": "Magnets and magnetism",
    "mitigasi_bencana_alam": "Natural disaster mitigation",
    "partikel_atom_dan_molekul_dasar": "Introductory particles, atoms, and molecules",
    "pemisahan_campuran_sederhana": "Simple mixture separation",
    "pencemaran_lingkungan": "Environmental pollution",
    "perpindahan_kalor": "Heat transfer",
    "perubahan_fisika_dan_kimia": "Physical and chemical changes",
    "perubahan_iklim_dan_mitigasi": "Climate change and mitigation",
    "pewarisan_sifat_dasar": "Introductory inheritance of traits",
    "rangkaian_listrik_sederhana": "Simple electrical circuits",
    "rantai_dan_jaring_makanan": "Food chains and food webs",
    "sifat_fisika_dan_kimia_zat": "Physical and chemical properties of matter",
    "sistem_peredaran_darah_manusia": "The human circulatory system",
    "sistem_pernapasan_manusia": "The human respiratory system",
    "sistem_reproduksi_manusia": "The human reproductive system",
    "struktur_bumi": "Earth's structure",
    "tata_surya": "The solar system",
    "tekanan": "Pressure",
    "usaha_dan_energi": "Work and energy",
    "wujud_zat": "States of matter",
    "zat_aditif_dan_zat_adiktif": "Additives and addictive substances",
    "adaptasi_makhluk_hidup_sederhana": "Simple adaptations of living things",
    "wujud_zat_dan_perubahannya": "States of matter and their changes",
    "gaya_gerak_dan_pengaruhnya": "Forces, motion, and their effects",
    "energi_cahaya_bunyi_dan_panas": "Light, sound, and heat energy",
    "bumi_bulan_matahari_dan_perubahannya": "Earth, moon, sun, and their changes",
    "sumber_daya_alam_dan_pemanfaatannya": "Natural resources and their uses",
    "rantai_makanan_dan_jaring_jaring_sederhana": "Food chains and simple food webs",
    "organ_pernapasan_pencernaan_dan_peredaran_darah_dasar": "Basic respiratory, digestive, and circulatory organs",
    "campuran_larutan_dan_perubahan_fisika_kimia_awal": "Mixtures, solutions, and introductory physical and chemical changes",
    "listrik_statis_dan_dinamis_sederhana": "Simple static and dynamic electricity",
    "magnet_dan_pemanfaatannya": "Magnets and their uses",
    "siklus_air_cuaca_iklim_dan_mitigasi_sederhana": "Water cycle, weather, climate, and simple mitigation",
    "bumi_tata_surya_dan_rotasi_revolusi": "Earth, the solar system, rotation, and revolution",
    "konservasi_energi_dan_lingkungan": "Energy conservation and the environment",
    "hakikat_sains_dan_kerja_ilmiah": "Nature of science and scientific work",
    "pengukuran_dalam_ipa": "Measurement in science",
    "variabel_bebas_terikat_kontrol": "Independent, dependent, and control variables",
    "merancang_penyelidikan_sederhana": "Designing simple investigations",
    "mengumpulkan_data_pengamatan": "Collecting observation data",
    "menganalisis_data_ipa": "Analyzing science data",
    "mengomunikasikan_hasil_penyelidikan": "Communicating investigation results",
    "ciri_makhluk_hidup": "Characteristics of living things",
    "klasifikasi_makhluk_hidup": "Classification of living things",
    "sel_sebagai_unit_kehidupan": "Cells as the unit of life",
    "jaringan_organ_dan_sistem_organ": "Tissues, organs, and organ systems",
    "sistem_pencernaan_manusia": "The human digestive system",
    "ekosistem_dan_aliran_energi": "Ecosystems and energy flow",
    "interaksi_makhluk_hidup_dan_lingkungan": "Interactions between living things and the environment",
    "zat_dan_perubahannya": "Matter and its changes",
    "unsur_senyawa_dan_campuran": "Elements, compounds, and mixtures",
    "asam_basa_dan_garam_sederhana": "Introductory acids, bases, and salts",
    "suhu_kalor_dan_perpindahannya": "Temperature, heat, and heat transfer",
    "gerak_gaya_dan_hukum_newton_awal": "Introductory motion, force, and Newton's laws",
    "usaha_energi_dan_pesawat_sederhana": "Work, energy, and simple machines",
    "getaran_gelombang_dan_bunyi": "Vibrations, waves, and sound",
    "cahaya_dan_optika_dasar": "Light and basic optics",
    "listrik_magnet_dan_pemanfaatannya": "Electricity, magnetism, and their uses",
    "bumi_tata_surya_dan_dampaknya_bagi_kehidupan": "Earth, the solar system, and their effects on life",
    "besaran_dan_satuan": "Quantities and units",
    "alat_ukur_dan_ketelitian": "Measuring instruments and precision",
    "angka_penting_dan_ketidakpastian": "Significant figures and uncertainty",
    "variabel_dalam_penyelidikan_fisika": "Variables in physics investigations",
    "grafik_data_pengukuran": "Graphs of measurement data",
    "perubahan_iklim_dan_pemanasan_global": "Climate change and global warming",
    "pencemaran_lingkungan_dari_sudut_pandang_fisika": "Environmental pollution from a physics perspective",
    "energi_dan_daya": "Energy and power",
    "energi_alternatif": "Alternative energy",
    "efisiensi_pemanfaatan_energi": "Efficient energy use",
    "laporan_penyelidikan_fisika": "Physics investigation reports",
    "arus_listrik_dan_rangkaian_dc": "Electric current and DC circuits",
    "fisika_inti": "Nuclear physics",
    "skalar_dan_vektor": "Scalars and vectors",
    "resultan_vektor": "Vector resultants",
    "kinematika_gerak_lurus": "Kinematics of straight-line motion",
    "gerak_dua_dimensi": "Two-dimensional motion",
    "dinamika_newton": "Newtonian dynamics",
    "gaya_gesek": "Friction",
    "usaha_energi_dan_daya_lanjut": "Advanced work, energy, and power",
    "momentum_dan_impuls": "Momentum and impulse",
    "gerak_melingkar": "Circular motion",
    "gravitasi_universal": "Universal gravitation",
    "medan_gravitasi_dan_satelit": "Gravitational fields and satellites",
    "fluida_statis": "Static fluids",
    "fluida_dinamis": "Dynamic fluids",
    "suhu_dan_kalor_lanjut": "Advanced temperature and heat",
    "teori_kinetik_gas": "The kinetic theory of gases",
    "termodinamika": "Thermodynamics",
    "getaran_harmonik_sederhana": "Simple harmonic motion",
    "gelombang_mekanik": "Mechanical waves",
    "gelombang_elektromagnetik": "Electromagnetic waves",
    "interferensi_difraksi_dan_polarisasi": "Interference, diffraction, and polarization",
    "alat_optik": "Optical instruments",
    "listrik_statis": "Static electricity",
    "medan_listrik_dan_hukum_coulomb": "Electric fields and Coulomb's law",
    "arus_tegangan_dan_hukum_ohm": "Current, voltage, and Ohm's law",
    "rangkaian_listrik": "Electric circuits",
    "medan_magnet_dan_induksi": "Magnetic fields and induction",
    "arus_bolak_balik_dan_transformator": "Alternating current and transformers",
    "struktur_atom": "Atomic structure",
    "hakikat_ilmu_kimia": "Nature of chemistry",
    "hukum_dasar_kimia_dalam_perhitungan_sederhana": "Basic chemistry laws in simple calculations",
    "hukum_kekekalan_massa": "The law of conservation of mass",
    "hukum_perbandingan_tetap": "The law of definite proportions",
    "keselamatan_kerja_laboratorium_kimia": "Safety in the chemistry laboratory",
    "kimia_dalam_kehidupan_sehari_hari": "Chemistry in everyday life",
    "kimia_lingkungan_dan_pemanasan_global": "Environmental chemistry and global warming",
    "klasifikasi_materi": "Classification of matter",
    "konfigurasi_elektron_sederhana": "Introductory electron configuration",
    "nanoteknologi_pengantar": "An introduction to nanotechnology",
    "nomor_atom_nomor_massa_isotop": "Atomic number, mass number, and isotopes",
    "partikel_subatom": "Subatomic particles",
    "persamaan_reaksi_kimia_sederhana": "Simple chemical equations",
    "perubahan_materi_dan_reaksi_kimia": "Changes in matter and chemical reactions",
    "sifat_fisika_dan_kimia_materi": "Physical and chemical properties of matter",
    "sistem_periodik_unsur_pengantar": "An introduction to the periodic table",
    "asam_basa": "Acids and bases",
    "bentuk_molekul_sederhana": "Simple molecular shapes",
    "elektrolisis": "Electrolysis",
    "entalpi_reaksi": "Enthalpy of reaction",
    "faktor_yang_memengaruhi_laju_reaksi": "Factors that affect reaction rate",
    "gugus_fungsi": "Functional groups",
    "hidrolisis_garam": "Salt hydrolysis",
    "hukum_hess": "Hess's law",
    "ikatan_ion": "Ionic bonding",
    "ikatan_kovalen": "Covalent bonding",
    "ikatan_logam": "Metallic bonding",
    "konsentrasi_larutan": "Solution concentration",
    "konsep_mol": "The mole concept",
    "korosi": "Corrosion",
    "laju_reaksi": "Reaction rate",
    "larutan_penyangga": "Buffer solutions",
    "massa_molar": "Molar mass",
    "orde_reaksi_pengantar": "An introduction to reaction order",
    "pereaksi_pembatas": "Limiting reactants",
    "ph_larutan": "Solution pH",
    "polimer_dan_pemanfaatannya": "Polymers and their uses",
    "prinsip_le_chatelier": "Le Chatelier's principle",
    "sel_volta": "Voltaic cells",
    "senyawa_karbon": "Carbon compounds",
    "sifat_fisik_materi_dari_struktur_partikel": "Physical properties of matter from particle structure",
    "stoikiometri_reaksi": "Reaction stoichiometry",
    "teori_tumbukan": "Collision theory",
    "termokimia": "Thermochemistry",
    "tetapan_kesetimbangan": "Equilibrium constants",
    "titrasi_asam_basa_dasar": "Introductory acid-base titration",
    "konfigurasi_elektron": "Electron configuration",
    "perkembangan_model_atom": "The development of atomic models",
    "ikatan_kimia": "Chemical bonding",
    "gaya_antarmolekul": "Intermolecular forces",
    "hukum_dasar_kimia": "Basic laws of chemistry",
    "stoikiometri_dasar": "Introductory stoichiometry",
    "larutan_dan_konsentrasi": "Solutions and concentration",
    "energi_dan_perubahan_reaksi": "Energy and reaction change",
    "laju_reaksi_dan_faktor_faktornya": "Reaction rate and its factors",
    "kesetimbangan_kimia_awal": "Introductory chemical equilibrium",
    "asam_basa_dan_ph": "Acids, bases, and pH",
    "hidrolisis_garam_dasar": "Introductory salt hydrolysis",
    "larutan_penyangga_dasar": "Introductory buffer solutions",
    "kelarutan_dan_ksp_awal": "Introductory solubility and Ksp",
    "redoks_dan_elektron": "Redox and electrons",
    "sel_elektrokimia": "Electrochemical cells",
    "kimia_karbon_dasar": "Introductory carbon chemistry",
    "hidrokarbon": "Hydrocarbons",
    "minyak_bumi_dan_petrokimia": "Petroleum and petrochemicals",
    "alkohol_eter_aldehida_keton_asam_karboksilat_ester": "Alcohols, ethers, aldehydes, ketones, carboxylic acids, and esters",
    "polimer_dan_biomolekul": "Polymers and biomolecules",
    "kimia_hijau_dan_lingkungan": "Green chemistry and the environment",
    "aliran_energi_ekosistem": "Energy flow in ecosystems",
    "bioteknologi_konvensional": "Conventional biotechnology",
    "bioteknologi_modern_pengantar": "An introduction to modern biotechnology",
    "daur_materi": "Matter cycles",
    "etika_teknologi_biologi": "Ethics in biological technology",
    "inovasi_teknologi_biologi": "Innovation in biological technology",
    "interaksi_biotik_abiotik": "Biotic and abiotic interactions",
    "keanekaragaman_hayati_indonesia": "Indonesia's biodiversity",
    "klasifikasi_dan_taksonomi_dasar": "Introductory classification and taxonomy",
    "komponen_ekosistem": "Components of ecosystems",
    "konservasi_keanekaragaman_hayati": "Biodiversity conservation",
    "pencegahan_penyakit_akibat_virus": "Preventing diseases caused by viruses",
    "peranan_keanekaragaman_hayati": "The importance of biodiversity",
    "peranan_virus_dalam_kehidupan": "The role of viruses in life",
    "perubahan_lingkungan_dan_solusi_lokal": "Environmental change and local solutions",
    "replikasi_virus": "Virus replication",
    "struktur_virus": "Virus structure",
    "tingkat_keanekaragaman_hayati": "Levels of biodiversity",
    "dna_gen_dan_kromosom": "DNA, genes, and chromosomes",
    "enzim": "Enzymes",
    "fotosintesis": "Photosynthesis",
    "gangguan_sistem_organ": "Disorders of organ systems",
    "homeostasis": "Homeostasis",
    "hukum_mendel": "Mendel's laws",
    "inovasi_teknologi_biologi_lanjut": "Advanced innovation in biological technology",
    "metabolisme_sel": "Cell metabolism",
    "mutasi": "Mutations",
    "organel_sel_dan_fungsinya": "Cell organelles and their functions",
    "osmosis_dan_difusi": "Osmosis and diffusion",
    "pembelahan_meiosis": "Meiosis",
    "pembelahan_mitosis": "Mitosis",
    "pertumbuhan_dan_perkembangan_manusia": "Human growth and development",
    "pertumbuhan_dan_perkembangan_tumbuhan": "Plant growth and development",
    "pola_hereditas_non_mendel": "Non-Mendelian inheritance patterns",
    "respirasi_sel": "Cell respiration",
    "seleksi_alam": "Natural selection",
    "sintesis_protein": "Protein synthesis",
    "sistem_ekskresi": "The excretory system",
    "sistem_endokrin": "The endocrine system",
    "sistem_imun": "The immune system",
    "sistem_pencernaan_lanjut": "Advanced digestive system topics",
    "sistem_peredaran_darah_lanjut": "Advanced circulatory system topics",
    "sistem_pernapasan_lanjut": "Advanced respiratory system topics",
    "sistem_reproduksi_lanjut": "Advanced reproductive system topics",
    "sistem_saraf": "The nervous system",
    "struktur_sel_eukariot_dan_prokariot": "Eukaryotic and prokaryotic cell structure",
    "teori_evolusi": "Theories of evolution",
    "transpor_membran": "Membrane transport",
    "struktur_dan_fungsi_sel": "Cell structure and function",
    "transport_membran_dan_homeostasis_sel": "Membrane transport and cellular homeostasis",
    "metabolisme_enzim_dan_energi_sel": "Metabolism, enzymes, and cellular energy",
    "pembelahan_sel_mitosis_meiosis": "Cell division: mitosis and meiosis",
    "genetika_dan_pewarisan_sifat": "Genetics and inheritance",
    "mutasi_dan_bioteknologi_dasar": "Mutations and introductory biotechnology",
    "evolusi_dan_keanekaragaman_hayati": "Evolution and biodiversity",
    "struktur_fungsi_jaringan_tumbuhan": "Plant tissue structure and function",
    "sistem_organ_tumbuhan": "Plant organ systems",
    "reproduksi_pertumbuhan_dan_perkembangan_tumbuhan": "Plant reproduction, growth, and development",
    "struktur_fungsi_jaringan_hewan": "Animal tissue structure and function",
    "sistem_organ_manusia": "Human organ systems",
    "regulasi_dan_koordinasi_tubuh": "Body regulation and coordination",
    "sistem_imun_dan_kesehatan": "The immune system and health",
    "ekologi_populasi_komunitas_ekosistem": "Ecology of populations, communities, and ecosystems",
    "aliran_energi_dan_siklus_biogeokimia": "Energy flow and biogeochemical cycles",
    "perubahan_lingkungan_dan_konservasi": "Environmental change and conservation",
    "klasifikasi_dan_filogeni": "Classification and phylogeny",
    "virus_bakteri_protista_jamur": "Viruses, bacteria, protists, and fungi",
    "animalia_dan_plantae": "Animalia and Plantae",
}


TOKEN_MAP = {
    "adaptasi": "adaptation",
    "air": "water",
    "alat": "tools",
    "aliran": "flow",
    "alam": "nature",
    "alternatif": "alternative",
    "analisis": "analysis",
    "anggota": "parts",
    "antarmolekul": "intermolecular",
    "arus": "current",
    "asam": "acids",
    "atom": "atoms",
    "bakteri": "bacteria",
    "basa": "bases",
    "bebas": "independent",
    "benda": "objects",
    "bertanya": "questioning",
    "biogeokimia": "biogeochemical",
    "bioteknologi": "biotechnology",
    "bolak": "alternating",
    "bumi": "earth",
    "bunyi": "sound",
    "campuran": "mixtures",
    "cahaya": "light",
    "ciri": "characteristics",
    "cuaca": "weather",
    "dan": "and",
    "dasar": "basic",
    "data": "data",
    "daya": "power",
    "difraksi": "diffraction",
    "dinamis": "dynamic",
    "dorongan": "pushes",
    "efisiensi": "efficiency",
    "ekologi": "ecology",
    "ekosistem": "ecosystems",
    "elektron": "electrons",
    "elektrokimia": "electrochemistry",
    "elektromagnetik": "electromagnetic",
    "energi": "energy",
    "enzim": "enzymes",
    "ester": "esters",
    "evolusi": "evolution",
    "fisika": "physics",
    "fluida": "fluids",
    "fotik": "optical",
    "fungsi": "function",
    "gas": "gases",
    "gelombang": "waves",
    "genetika": "genetics",
    "gerak": "motion",
    "gaya": "force",
    "global": "global",
    "grafik": "graphs",
    "gravitasi": "gravity",
    "hakikat": "nature",
    "harmonik": "harmonic",
    "hewan": "animals",
    "hidrolisis": "hydrolysis",
    "hidrokarbon": "hydrocarbons",
    "hidup": "living things",
    "hijau": "green",
    "hasil": "results",
    "homeostasis": "homeostasis",
    "hukum": "laws",
    "ikatan": "bonding",
    "iklim": "climate",
    "ilmiah": "scientific",
    "imun": "immune",
    "impuls": "impulse",
    "induksi": "induction",
    "interaksi": "interactions",
    "interferensi": "interference",
    "investigasi": "investigation",
    "jamur": "fungi",
    "keanekaragaman": "biodiversity",
    "kehidupan": "life",
    "kebutuhannya": "needs",
    "kedudukan": "position",
    "kelarutan": "solubility",
    "kesehatan": "health",
    "kesetimbangan": "equilibrium",
    "ketelitian": "precision",
    "ketidakpastian": "uncertainty",
    "kimia": "chemistry",
    "kinematika": "kinematics",
    "kinetik": "kinetic",
    "klasifikasi": "classification",
    "komunitas": "communities",
    "konsentrasi": "concentration",
    "konservasi": "conservation",
    "kontrol": "control",
    "koordinasi": "coordination",
    "langit": "sky",
    "laporan": "reports",
    "larutan": "solutions",
    "laju": "rate",
    "lingkungan": "environment",
    "listrik": "electricity",
    "makhluk": "living things",
    "magnet": "magnets",
    "mahluk": "living things",
    "malam": "night",
    "manusia": "human",
    "matahari": "sun",
    "medan": "fields",
    "meiosis": "meiosis",
    "membran": "membrane",
    "mengalisis": "analyzing",
    "menganalisis": "analyzing",
    "mengomunikasikan": "communicating",
    "mengumpulkan": "collecting",
    "menjaga": "protecting",
    "merancang": "designing",
    "metabolisme": "metabolism",
    "mikro": "micro",
    "minyak": "petroleum",
    "mitigasi": "mitigation",
    "mitosis": "mitosis",
    "model": "models",
    "musim": "seasons",
    "mutasi": "mutations",
    "newton": "Newton",
    "objek": "objects",
    "observasi": "observation",
    "ohm": "Ohm",
    "optik": "optics",
    "organ": "organs",
    "pancaindra": "the senses",
    "panas": "heat",
    "pemanasan": "warming",
    "pemanfaatan": "use",
    "pembelahan": "division",
    "pencernaan": "digestion",
    "pencemaran": "pollution",
    "pengamatan": "observation",
    "pengukuran": "measurement",
    "penyelidikan": "investigation",
    "peredaran": "circulation",
    "perkembangan": "development",
    "pernapasan": "respiration",
    "perubahan": "changes",
    "petrokimia": "petrochemicals",
    "pewarisan": "inheritance",
    "ph": "pH",
    "planet": "planets",
    "plantae": "Plantae",
    "polarisasi": "polarization",
    "polimer": "polymers",
    "populasi": "populations",
    "protista": "protists",
    "reaksi": "reaction",
    "reproduksi": "reproduction",
    "resultan": "resultant",
    "revolusi": "revolution",
    "rotasi": "rotation",
    "sains": "science",
    "sal": "salts",
    "sampah": "waste",
    "satelit": "satellites",
    "sederhana": "simple",
    "sel": "cells",
    "senyawa": "compounds",
    "sifat": "properties",
    "siklus": "cycles",
    "siang": "day",
    "sistem": "systems",
    "skalar": "scalars",
    "suhu": "temperature",
    "sumber": "resources",
    "surya": "solar",
    "statis": "static",
    "stoikiometri": "stoichiometry",
    "struktur": "structure",
    "sudut": "perspective",
    "suku": "terms",
    "suhu": "temperature",
    "syarat": "conditions",
    "tata": "solar",
    "tarikan": "pulls",
    "tegangan": "voltage",
    "teori": "theory",
    "terikat": "dependent",
    "termodinamika": "thermodynamics",
    "tumbuhan": "plants",
    "tubuh": "body",
    "udara": "air",
    "unit": "unit",
    "unsur": "elements",
    "usaha": "work",
    "variabel": "variables",
    "vektor": "vectors",
    "virus": "viruses",
    "wujud": "states",
    "zat": "matter",
}


PROMPT_TEMPLATES = [
    "Which topic best matches this idea: {description}?",
    "A lesson about {description} belongs to which topic?",
    "Which topic would help a student learn about {description}?",
    "Which science topic focuses on {description}?",
]


def suffix_from_node_id(node_id: str) -> str:
    return "_".join(node_id.split("_")[3:])


def translate_suffix(suffix: str) -> str:
    if suffix in PHRASE_OVERRIDES:
        return PHRASE_OVERRIDES[suffix]

    words = [TOKEN_MAP.get(token, token) for token in suffix.split("_")]
    text = " ".join(words).replace("  ", " ").strip()
    return text[:1].upper() + text[1:]


def describe_topic(title: str) -> str:
    lower = title.lower()
    if "observation" in lower or "questioning" in lower or "scientific" in lower or "investigation" in lower:
        return "scientific observation, evidence, and investigation"
    if "measurement" in lower or "precision" in lower or "uncertainty" in lower or "graphs" in lower:
        return "measuring carefully and interpreting data"
    if "living things" in lower or "animals" in lower or "plants" in lower or "biodiversity" in lower:
        return "living things and how they survive"
    if "cells" in lower or "tissues" in lower or "organs" in lower or "human" in lower or "immune" in lower:
        return "body structures and life processes"
    if "ecology" in lower or "ecosystems" in lower or "environment" in lower or "conservation" in lower:
        return "ecosystems, environment, and conservation"
    if "matter" in lower or "states" in lower or "mixtures" in lower or "solutions" in lower:
        return "matter, mixtures, and how materials change"
    if "atoms" in lower or "bonding" in lower or "stoichiometry" in lower:
        return "particles, substances, and chemical relationships"
    if "acids" in lower or "bases" in lower or "ph" in lower or "equilibrium" in lower:
        return "chemical reactions and solution behavior"
    if "energy" in lower or "heat" in lower or "temperature" in lower or "thermodynamics" in lower:
        return "energy, heat, and how systems change"
    if "motion" in lower or "force" in lower or "newton" in lower or "friction" in lower:
        return "forces and motion"
    if "electricity" in lower or "voltage" in lower or "ohm" in lower or "magnetic" in lower:
        return "electricity and magnetism"
    if "waves" in lower or "sound" in lower or "light" in lower or "optics" in lower:
        return "waves, sound, and light"
    if "earth" in lower or "solar" in lower or "sky" in lower or "climate" in lower:
        return "Earth systems, weather, and space"
    return lower


def difficulty_for_phase(phase: str, assessment_type: str) -> str:
    matrix = {
        "A": {"pretest": "easy", "daily_quiz": "easy", "posttest": "easy", "workspace_quiz": "easy"},
        "B": {"pretest": "easy", "daily_quiz": "easy", "posttest": "medium", "workspace_quiz": "easy"},
        "C": {"pretest": "easy", "daily_quiz": "medium", "posttest": "medium", "workspace_quiz": "easy"},
        "D": {"pretest": "medium", "daily_quiz": "medium", "posttest": "hard", "workspace_quiz": "medium"},
        "E": {"pretest": "medium", "daily_quiz": "medium", "posttest": "hard", "workspace_quiz": "medium"},
        "F": {"pretest": "medium", "daily_quiz": "hard", "posttest": "hard", "workspace_quiz": "medium"},
    }
    return matrix[phase][assessment_type]


def cognitive_for_phase(phase: str, assessment_type: str) -> str:
    matrix = {
        "A": {"pretest": "understand", "daily_quiz": "remember", "posttest": "understand", "workspace_quiz": "remember"},
        "B": {"pretest": "understand", "daily_quiz": "remember", "posttest": "apply", "workspace_quiz": "remember"},
        "C": {"pretest": "understand", "daily_quiz": "understand", "posttest": "apply", "workspace_quiz": "remember"},
        "D": {"pretest": "apply", "daily_quiz": "understand", "posttest": "analyze", "workspace_quiz": "understand"},
        "E": {"pretest": "apply", "daily_quiz": "understand", "posttest": "analyze", "workspace_quiz": "understand"},
        "F": {"pretest": "apply", "daily_quiz": "apply", "posttest": "analyze", "workspace_quiz": "understand"},
    }
    return matrix[phase][assessment_type]


def choose_distractors(node: dict, titles_by_id: dict[str, str], peers: list[dict]) -> list[str]:
    same_domain = [peer for peer in peers if peer["id"] != node["id"] and peer.get("domain") == node.get("domain")]
    fallback = [peer for peer in peers if peer["id"] != node["id"]]
    pool = same_domain if len(same_domain) >= 3 else fallback
    pool = sorted(pool, key=lambda peer: peer["id"])
    picks = []
    for peer in pool:
        title = titles_by_id[peer["id"]]
        if title not in picks:
            picks.append(title)
        if len(picks) == 3:
            break
    while len(picks) < 3:
        picks.append("General science topic")
    return picks


def question_item(node: dict, config: dict, assessment_type: str, distractors: list[str], number: int) -> dict:
    suffix = suffix_from_node_id(node["id"])
    title = translate_suffix(suffix)
    description = describe_topic(title)
    templates = ASSESSMENT_VARIANTS[assessment_type]["prompt_templates"]
    prompt = templates[number % len(templates)].format(description=description)

    options = [title] + distractors[:3]
    random.Random(node["id"]).shuffle(options)
    labels = ["A", "B", "C", "D"]
    option_objs = [{"label": label, "text": text} for label, text in zip(labels, options)]
    answer_key = next(obj["label"] for obj in option_objs if obj["text"] == title)

    return {
        "id": f"{config['subject_short']}_{config['level_short']}_{suffix[:24]}_{ASSESSMENT_VARIANTS[assessment_type]['short']}_{number:03d}",
        "subject_code": node["subject"],
        "concept_code": suffix,
        "concept_title": title,
        "education_level": config["education_level"],
        "grade_band": config["grade_band"],
        "language": "en",
        "assessment_types": [assessment_type],
        "question_type": "multiple_choice",
        "difficulty": difficulty_for_phase(node["phase"], assessment_type),
        "cognitive_level": cognitive_for_phase(node["phase"], assessment_type),
        "prompt": prompt,
        "helper_text": ASSESSMENT_VARIANTS[assessment_type]["helper_text"],
        "options": option_objs,
        "answer_key": answer_key,
        "explanation": f"The correct topic is {title} because it best matches the science idea in the prompt.",
        "rubric": {
            "correct": f"Learner identifies the topic {title} from its core idea.",
            "common_misconceptions": [
                "Chooses a nearby topic from the same strand without checking the key idea.",
                "Focuses on one familiar word instead of the full topic meaning."
            ]
        },
        "tags": [node["subject"], config["education_level"], node["phase"].lower(), suffix, assessment_type, "topic_identification"],
        "status": "active",
        "metadata": {
            "source_pack": "baseline_generated",
            "estimated_seconds": 45
        }
    }


def build_seed(subject: str, nodes: list[dict]) -> dict:
    config = SUBJECT_GROUPS[subject]
    ordered_nodes = sorted(nodes, key=lambda n: (n["phase"], n["id"]))
    titles_by_id = {node["id"]: translate_suffix(suffix_from_node_id(node["id"])) for node in ordered_nodes}
    items = []
    counters = {assessment_type: 1 for assessment_type in ASSESSMENT_VARIANTS}
    for node in ordered_nodes:
        distractors = choose_distractors(node, titles_by_id, ordered_nodes)
        for assessment_type in ("pretest", "daily_quiz", "posttest", "workspace_quiz"):
            items.append(question_item(node, config, assessment_type, distractors, counters[assessment_type]))
            counters[assessment_type] += 1

    return {
        "version": "2026-05-16",
        "source": "wicara_question_bank_seed_v1",
        "language": "en",
        "subject_code": subject,
        "education_level": config["education_level"],
        "grade_band": config["grade_band"],
        "items": items,
    }


def main() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    nodes = [node for node in graph["nodes"] if node.get("is_assessable")]
    SEED_DIR.mkdir(parents=True, exist_ok=True)

    for subject, config in SUBJECT_GROUPS.items():
        subject_nodes = [node for node in nodes if node.get("subject") == subject and node.get("phase") in config["phases"]]
        seed = build_seed(subject, subject_nodes)
        out_path = SEED_DIR / f"{config['filename_subject']}.{config['education_level']}.all_topics.v1.json"
        out_path.write_text(json.dumps(seed, ensure_ascii=True, indent=2), encoding="utf-8")
        print(f"{out_path.name}: {len(seed['items'])} items")


if __name__ == "__main__":
    main()
