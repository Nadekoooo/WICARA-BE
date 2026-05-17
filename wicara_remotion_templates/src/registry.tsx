
import React from 'react';
import {Composition} from 'remotion';
import {RemotionConceptSpec} from './types';
import * as Templates from './Templates';

export const conceptSpecs = [
  {
    "id": "remotion_v2_005_ecosystem_environment_system",
    "row_index": 5,
    "concept_type": "ecosystem_environment_system",
    "concept_type_label_id": "Ekosistem, interaksi, pencemaran, dan iklim",
    "template_id": "remotion.bio_ecosystem_network.v1",
    "component": "EcosystemNetworkVideo",
    "archetype": "ecosystem_network",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Ekosistem, interaksi, pencemaran, dan iklim",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `ecosystem_environment_system`.",
    "keyIdea": "Ekosistem adalah jaringan aliran energi, materi, dan dampak lingkungan.",
    "steps": [
      {
        "id": "context",
        "start": 90,
        "duration": 170,
        "title": "1. Ekosistem sebagai jaringan",
        "narration": "Kita mulai dengan melihat ekosistem sebagai jaringan, bukan kumpulan makhluk hidup yang terpisah."
      },
      {
        "id": "sun",
        "start": 260,
        "duration": 170,
        "title": "2. Energi masuk dari Matahari",
        "narration": "Energi utama masuk melalui cahaya matahari dan ditangkap oleh produsen."
      },
      {
        "id": "flow",
        "start": 430,
        "duration": 170,
        "title": "3. Energi berpindah antar organisme",
        "narration": "Energi bergerak dari produsen ke konsumen melalui hubungan makan-dimakan."
      },
      {
        "id": "decomposer",
        "start": 600,
        "duration": 170,
        "title": "4. Pengurai mengembalikan materi",
        "narration": "Pengurai memecah sisa makhluk hidup sehingga materi kembali ke lingkungan."
      },
      {
        "id": "stressor",
        "start": 770,
        "duration": 170,
        "title": "5. Gangguan menyebar melalui jaringan",
        "narration": "Pencemaran atau perubahan iklim dapat memengaruhi banyak komponen sekaligus."
      },
      {
        "id": "balance",
        "start": 940,
        "duration": 170,
        "title": "6. Keseimbangan perlu dijaga",
        "narration": "Ekosistem lebih stabil jika aliran energi dan daur materi tidak terganggu."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Rangkai kembali ide utama",
        "narration": "Jaringan ekosistem menunjukkan hubungan antara energi, materi, interaksi, dan dampak lingkungan."
      }
    ],
    "visual": {
      "chain": [
        "Matahari",
        "Produsen",
        "Konsumen I",
        "Konsumen II",
        "Pengurai"
      ],
      "stressors": [
        "Polusi",
        "Iklim",
        "Deforestasi"
      ]
    },
    "summarySequence": [
      "Matahari",
      "Produsen",
      "Konsumen",
      "Pengurai",
      "Gangguan",
      "Keseimbangan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_006_organ_system_flow_regulation",
    "row_index": 6,
    "concept_type": "organ_system_flow_regulation",
    "concept_type_label_id": "Sistem organ, aliran, dan regulasi tubuh",
    "template_id": "remotion.bio_organ_system_flow.v1",
    "component": "OrganSystemFlowVideo",
    "archetype": "organ_flow",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Sistem organ, aliran, dan regulasi tubuh",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `organ_system_flow_regulation`.",
    "keyIdea": "Tubuh bekerja lewat aliran zat dan koordinasi antar sistem organ.",
    "steps": [
      {
        "id": "body",
        "start": 90,
        "duration": 170,
        "title": "1. Tubuh sebagai sistem terpadu",
        "narration": "Tubuh manusia tersusun dari sistem organ yang saling terhubung."
      },
      {
        "id": "input",
        "start": 260,
        "duration": 170,
        "title": "2. Bahan masuk ke tubuh",
        "narration": "Makanan dan oksigen masuk melalui sistem yang berbeda."
      },
      {
        "id": "transport",
        "start": 430,
        "duration": 170,
        "title": "3. Darah mengangkut zat penting",
        "narration": "Sistem peredaran darah mendistribusikan nutrisi dan oksigen ke seluruh tubuh."
      },
      {
        "id": "use",
        "start": 600,
        "duration": 170,
        "title": "4. Sel memakai bahan",
        "narration": "Sel menggunakan bahan tersebut untuk menghasilkan energi dan menjalankan fungsi hidup."
      },
      {
        "id": "waste",
        "start": 770,
        "duration": 170,
        "title": "5. Zat sisa dikeluarkan",
        "narration": "Sistem ekskresi membantu mengeluarkan zat sisa agar tubuh tetap seimbang."
      },
      {
        "id": "regulate",
        "start": 940,
        "duration": 170,
        "title": "6. Regulasi menjaga koordinasi",
        "narration": "Sistem saraf dan hormon mengatur kerja organ agar tetap sesuai kebutuhan."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Sistem tubuh bekerja bersama",
        "narration": "Aliran dan regulasi menjelaskan mengapa organ tidak bekerja sendiri-sendiri."
      }
    ],
    "visual": {
      "systems": [
        "Pencernaan",
        "Pernapasan",
        "Peredaran darah",
        "Ekskresi"
      ],
      "flows": [
        "nutrisi",
        "oksigen",
        "darah",
        "zat sisa"
      ]
    },
    "summarySequence": [
      "Input",
      "Transport",
      "Pemakaian",
      "Zat sisa",
      "Regulasi",
      "Homeostasis"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_011_earth_space_system_model",
    "row_index": 11,
    "concept_type": "earth_space_system_model",
    "concept_type_label_id": "Bumi, tata surya, gerak langit, dan kebencanaan",
    "template_id": "remotion.earth_space_system.v1",
    "component": "EarthSpaceSystemVideo",
    "archetype": "orbit_system",
    "domain": "earth",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Bumi, tata surya, gerak langit, dan kebencanaan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `earth_space_system_model`.",
    "keyIdea": "Rotasi dan revolusi menjelaskan pola langit yang tampak dari Bumi.",
    "steps": [
      {
        "id": "space",
        "start": 90,
        "duration": 170,
        "title": "1. Benda langit punya posisi",
        "narration": "Matahari, Bumi, dan Bulan berada pada susunan yang terus berubah."
      },
      {
        "id": "rotate",
        "start": 260,
        "duration": 170,
        "title": "2. Bumi berotasi",
        "narration": "Rotasi Bumi membuat sisi yang menghadap Matahari mengalami siang."
      },
      {
        "id": "night",
        "start": 430,
        "duration": 170,
        "title": "3. Sisi lain mengalami malam",
        "narration": "Bagian yang membelakangi Matahari berada dalam kondisi malam."
      },
      {
        "id": "moon",
        "start": 600,
        "duration": 170,
        "title": "4. Bulan mengorbit Bumi",
        "narration": "Gerak Bulan mengubah posisi relatif terhadap Bumi dan Matahari."
      },
      {
        "id": "phenomena",
        "start": 770,
        "duration": 170,
        "title": "5. Fenomena langit muncul",
        "narration": "Gerak ini menjelaskan fase Bulan, gerhana, dan pola langit lain."
      },
      {
        "id": "earth",
        "start": 940,
        "duration": 170,
        "title": "6. Hubungkan dengan kebumian",
        "narration": "Model ruang angkasa membantu membaca waktu, musim, dan peristiwa alam."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Rangkai model tata surya",
        "narration": "Gerak langit menjadi masuk akal ketika kita memodelkan posisi dan arah gerak."
      }
    ],
    "visual": {
      "objects": [
        "Matahari",
        "Bumi",
        "Bulan"
      ],
      "phenomena": [
        "Siang-malam",
        "Musim",
        "Gerhana"
      ]
    },
    "summarySequence": [
      "Matahari",
      "Rotasi Bumi",
      "Siang",
      "Malam",
      "Bulan",
      "Fenomena"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_012_chemical_bonding_molecular_structure",
    "row_index": 12,
    "concept_type": "chemical_bonding_molecular_structure",
    "concept_type_label_id": "Ikatan kimia, bentuk molekul, dan gaya antarmolekul",
    "template_id": "remotion.chem_bonding_molecule.v1",
    "component": "ChemBondingMoleculeVideo",
    "archetype": "bonding_molecule",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Ikatan kimia, bentuk molekul, dan gaya antarmolekul",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `chemical_bonding_molecular_structure`.",
    "keyIdea": "Ikatan terbentuk melalui interaksi elektron dan menentukan bentuk molekul.",
    "steps": [
      {
        "id": "atoms",
        "start": 90,
        "duration": 170,
        "title": "1. Atom memiliki elektron valensi",
        "narration": "Atom bereaksi melalui elektron terluar yang menentukan kecenderungan ikatan."
      },
      {
        "id": "approach",
        "start": 260,
        "duration": 170,
        "title": "2. Atom saling mendekat",
        "narration": "Ketika atom mendekat, elektron dan inti saling berinteraksi."
      },
      {
        "id": "bond",
        "start": 430,
        "duration": 170,
        "title": "3. Ikatan terbentuk",
        "narration": "Ikatan dapat terjadi karena elektron dibagi bersama atau berpindah."
      },
      {
        "id": "shape",
        "start": 600,
        "duration": 170,
        "title": "4. Pasangan elektron menentukan bentuk",
        "narration": "Tolak-menolak pasangan elektron membuat molekul memiliki geometri tertentu."
      },
      {
        "id": "polarity",
        "start": 770,
        "duration": 170,
        "title": "5. Bentuk memengaruhi sifat",
        "narration": "Bentuk dan kepolaran molekul ikut menentukan sifat fisik zat."
      },
      {
        "id": "compare",
        "start": 940,
        "duration": 170,
        "title": "6. Bandingkan jenis ikatan",
        "narration": "Ikatan ionik, kovalen, dan polar memiliki ciri yang berbeda."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Hubungkan mikro ke sifat zat",
        "narration": "Struktur molekul membantu menjelaskan sifat zat yang kita amati."
      }
    ],
    "visual": {
      "atoms": [
        "H",
        "O",
        "H"
      ],
      "bondTypes": [
        "ionik",
        "kovalen",
        "polar"
      ],
      "geometry": "bengkok"
    },
    "summarySequence": [
      "Elektron valensi",
      "Atom mendekat",
      "Ikatan",
      "Bentuk molekul",
      "Sifat zat"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_019_human_body_system_flow",
    "row_index": 19,
    "concept_type": "human_body_system_flow",
    "concept_type_label_id": "Sistem organ manusia",
    "template_id": "remotion.bio_flow_system.v1",
    "component": "HumanBodyFlowVideo",
    "archetype": "human_body_flow",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Sistem organ manusia",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `human_body_system_flow`.",
    "keyIdea": "Aktivitas harian melibatkan beberapa sistem tubuh sekaligus.",
    "steps": [
      {
        "id": "body",
        "start": 90,
        "duration": 170,
        "title": "1. Kenali sistem utama",
        "narration": "Tubuh memiliki beberapa sistem yang bekerja bersama agar kita bisa hidup dan bergerak."
      },
      {
        "id": "food",
        "start": 260,
        "duration": 170,
        "title": "2. Makanan menjadi nutrisi",
        "narration": "Sistem pencernaan memecah makanan menjadi nutrisi yang dapat diserap."
      },
      {
        "id": "oxygen",
        "start": 430,
        "duration": 170,
        "title": "3. Oksigen masuk lewat pernapasan",
        "narration": "Sistem pernapasan membawa oksigen ke tubuh."
      },
      {
        "id": "blood",
        "start": 600,
        "duration": 170,
        "title": "4. Darah mengirim bahan",
        "narration": "Darah membawa oksigen dan nutrisi menuju sel."
      },
      {
        "id": "muscle",
        "start": 770,
        "duration": 170,
        "title": "5. Otot memakai energi",
        "narration": "Otot menggunakan energi untuk bergerak dan melakukan aktivitas."
      },
      {
        "id": "health",
        "start": 940,
        "duration": 170,
        "title": "6. Kesehatan menjaga aliran",
        "narration": "Kebiasaan sehat membantu sistem tubuh bekerja optimal."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Sistem tubuh saling mendukung",
        "narration": "Satu aktivitas sederhana bisa melibatkan banyak sistem organ sekaligus."
      }
    ],
    "visual": {
      "systems": [
        "Pencernaan",
        "Pernapasan",
        "Darah",
        "Otot"
      ],
      "outputs": [
        "nutrisi",
        "oksigen",
        "energi"
      ]
    },
    "summarySequence": [
      "Makan",
      "Bernapas",
      "Darah mengalir",
      "Energi",
      "Gerak",
      "Kesehatan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_023_biodiversity_classification_conservation",
    "row_index": 23,
    "concept_type": "biodiversity_classification_conservation",
    "concept_type_label_id": "Keanekaragaman, klasifikasi, dan konservasi",
    "template_id": "remotion.bio_taxonomy_biodiversity.v1",
    "component": "TaxonomyBiodiversityVideo",
    "archetype": "taxonomy_biodiversity",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Keanekaragaman, klasifikasi, dan konservasi",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `biodiversity_classification_conservation`.",
    "keyIdea": "Klasifikasi menata keragaman, konservasi menjaga keberlangsungannya.",
    "steps": [
      {
        "id": "diversity",
        "start": 90,
        "duration": 170,
        "title": "1. Keanekaragaman terlihat di alam",
        "narration": "Makhluk hidup memiliki bentuk, habitat, dan peran yang sangat beragam."
      },
      {
        "id": "group",
        "start": 260,
        "duration": 170,
        "title": "2. Ciri digunakan untuk mengelompokkan",
        "narration": "Organisme dikelompokkan berdasarkan ciri yang mirip."
      },
      {
        "id": "levels",
        "start": 430,
        "duration": 170,
        "title": "3. Klasifikasi bertingkat",
        "narration": "Taksonomi menyusun organisme dari kelompok umum ke kelompok yang lebih khusus."
      },
      {
        "id": "habitat",
        "start": 600,
        "duration": 170,
        "title": "4. Habitat menyimpan keragaman",
        "narration": "Setiap habitat mendukung kombinasi organisme yang berbeda."
      },
      {
        "id": "threat",
        "start": 770,
        "duration": 170,
        "title": "5. Ancaman mengurangi keragaman",
        "narration": "Kerusakan habitat dapat menurunkan jumlah spesies."
      },
      {
        "id": "conserve",
        "start": 940,
        "duration": 170,
        "title": "6. Konservasi menjaga kehidupan",
        "narration": "Konservasi dilakukan untuk melindungi habitat dan organisme."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Klasifikasi dan konservasi saling melengkapi",
        "narration": "Kita mengelompokkan makhluk hidup untuk memahami dan menjaganya."
      }
    ],
    "visual": {
      "levels": [
        "Kingdom",
        "Filum",
        "Kelas",
        "Ordo",
        "Famili"
      ],
      "habitats": [
        "Hutan",
        "Laut",
        "Savana"
      ]
    },
    "summarySequence": [
      "Keragaman",
      "Ciri",
      "Taksonomi",
      "Habitat",
      "Ancaman",
      "Konservasi"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_024_biotechnology_process_ethics",
    "row_index": 24,
    "concept_type": "biotechnology_process_ethics",
    "concept_type_label_id": "Bioteknologi, inovasi, dan etika",
    "template_id": "remotion.bio_biotech_process.v1",
    "component": "BiotechProcessVideo",
    "archetype": "biotech_process",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Bioteknologi, inovasi, dan etika",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `biotechnology_process_ethics`.",
    "keyIdea": "Bioteknologi mengubah proses biologis menjadi produk, tetapi perlu pertimbangan etika.",
    "steps": [
      {
        "id": "material",
        "start": 90,
        "duration": 170,
        "title": "1. Mulai dari bahan biologis",
        "narration": "Bioteknologi memanfaatkan organisme, sel, atau molekul biologis."
      },
      {
        "id": "process",
        "start": 260,
        "duration": 170,
        "title": "2. Proses dikendalikan",
        "narration": "Proses biologis dikondisikan agar menghasilkan produk tertentu."
      },
      {
        "id": "product",
        "start": 430,
        "duration": 170,
        "title": "3. Produk dimanfaatkan",
        "narration": "Produk bioteknologi bisa dipakai untuk pangan, kesehatan, dan lingkungan."
      },
      {
        "id": "modern",
        "start": 600,
        "duration": 170,
        "title": "4. Teknologi modern memperluas kemampuan",
        "narration": "Bioteknologi modern dapat memodifikasi proses pada tingkat gen atau sel."
      },
      {
        "id": "risk",
        "start": 770,
        "duration": 170,
        "title": "5. Ada risiko yang harus dinilai",
        "narration": "Keamanan, dampak lingkungan, dan akses menjadi pertimbangan penting."
      },
      {
        "id": "ethics",
        "start": 940,
        "duration": 170,
        "title": "6. Etika mengarahkan inovasi",
        "narration": "Inovasi perlu digunakan secara bertanggung jawab."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Proses dan etika berjalan bersama",
        "narration": "Bioteknologi bukan hanya soal produk, tetapi juga keputusan penggunaannya."
      }
    ],
    "visual": {
      "pipeline": [
        "Bahan biologis",
        "Proses",
        "Produk"
      ],
      "examples": [
        "Tempe",
        "Insulin",
        "Kultur jaringan"
      ],
      "ethics": [
        "Keamanan",
        "Akses",
        "Lingkungan"
      ]
    },
    "summarySequence": [
      "Bahan",
      "Proses",
      "Produk",
      "Manfaat",
      "Risiko",
      "Etika"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_025_ecosystem_interaction_energy_matter",
    "row_index": 25,
    "concept_type": "ecosystem_interaction_energy_matter",
    "concept_type_label_id": "Ekosistem, interaksi, aliran energi, dan daur materi",
    "template_id": "remotion.bio_ecosystem_network.v1",
    "component": "EcosystemNetworkVideo",
    "archetype": "ecosystem_network",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Ekosistem, interaksi, aliran energi, dan daur materi",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `ecosystem_interaction_energy_matter`.",
    "keyIdea": "Ekosistem adalah jaringan aliran energi, materi, dan dampak lingkungan.",
    "steps": [
      {
        "id": "context",
        "start": 90,
        "duration": 170,
        "title": "1. Ekosistem sebagai jaringan",
        "narration": "Kita mulai dengan melihat ekosistem sebagai jaringan, bukan kumpulan makhluk hidup yang terpisah."
      },
      {
        "id": "sun",
        "start": 260,
        "duration": 170,
        "title": "2. Energi masuk dari Matahari",
        "narration": "Energi utama masuk melalui cahaya matahari dan ditangkap oleh produsen."
      },
      {
        "id": "flow",
        "start": 430,
        "duration": 170,
        "title": "3. Energi berpindah antar organisme",
        "narration": "Energi bergerak dari produsen ke konsumen melalui hubungan makan-dimakan."
      },
      {
        "id": "decomposer",
        "start": 600,
        "duration": 170,
        "title": "4. Pengurai mengembalikan materi",
        "narration": "Pengurai memecah sisa makhluk hidup sehingga materi kembali ke lingkungan."
      },
      {
        "id": "stressor",
        "start": 770,
        "duration": 170,
        "title": "5. Gangguan menyebar melalui jaringan",
        "narration": "Pencemaran atau perubahan iklim dapat memengaruhi banyak komponen sekaligus."
      },
      {
        "id": "balance",
        "start": 940,
        "duration": 170,
        "title": "6. Keseimbangan perlu dijaga",
        "narration": "Ekosistem lebih stabil jika aliran energi dan daur materi tidak terganggu."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Rangkai kembali ide utama",
        "narration": "Jaringan ekosistem menunjukkan hubungan antara energi, materi, interaksi, dan dampak lingkungan."
      }
    ],
    "visual": {
      "chain": [
        "Matahari",
        "Produsen",
        "Konsumen I",
        "Konsumen II",
        "Pengurai"
      ],
      "stressors": [
        "Polusi",
        "Iklim",
        "Deforestasi"
      ]
    },
    "summarySequence": [
      "Matahari",
      "Produsen",
      "Konsumen",
      "Pengurai",
      "Gangguan",
      "Keseimbangan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_026_atomic_structure_periodic_model",
    "row_index": 26,
    "concept_type": "atomic_structure_periodic_model",
    "concept_type_label_id": "Atom, elektron, isotop, dan sistem periodik",
    "template_id": "remotion.chem_atomic_periodic.v1",
    "component": "AtomicPeriodicVideo",
    "archetype": "atomic_periodic",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Atom, elektron, isotop, dan sistem periodik",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `atomic_structure_periodic_model`.",
    "keyIdea": "Konfigurasi elektron menghubungkan struktur atom dengan posisi unsur pada tabel periodik.",
    "steps": [
      {
        "id": "nucleus",
        "start": 90,
        "duration": 170,
        "title": "1. Atom memiliki inti",
        "narration": "Inti atom berisi proton dan neutron yang menentukan identitas serta massa atom."
      },
      {
        "id": "electron",
        "start": 260,
        "duration": 170,
        "title": "2. Elektron berada di sekitar inti",
        "narration": "Elektron menempati tingkat energi tertentu di sekitar inti."
      },
      {
        "id": "configuration",
        "start": 430,
        "duration": 170,
        "title": "3. Konfigurasi elektron terbentuk",
        "narration": "Susunan elektron menentukan elektron valensi suatu unsur."
      },
      {
        "id": "periodic",
        "start": 600,
        "duration": 170,
        "title": "4. Posisi periodik punya pola",
        "narration": "Tabel periodik menyusun unsur berdasarkan nomor atom dan kemiripan sifat."
      },
      {
        "id": "group",
        "start": 770,
        "duration": 170,
        "title": "5. Golongan menunjukkan kemiripan",
        "narration": "Unsur dalam golongan yang sama sering memiliki elektron valensi serupa."
      },
      {
        "id": "property",
        "start": 940,
        "duration": 170,
        "title": "6. Struktur menjelaskan sifat",
        "narration": "Sifat kimia unsur dapat ditelusuri ke struktur elektronnya."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Hubungkan atom dan tabel",
        "narration": "Model atom memberi alasan mengapa tabel periodik memiliki pola."
      }
    ],
    "visual": {
      "element": "Na",
      "subparticles": [
        "Proton",
        "Neutron",
        "Elektron"
      ],
      "groups": [
        "Gol. 1",
        "Gol. 17",
        "Gol. 18"
      ]
    },
    "summarySequence": [
      "Inti",
      "Elektron",
      "Konfigurasi",
      "Tabel periodik",
      "Golongan",
      "Sifat"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_028_acid_base_ph_titration",
    "row_index": 28,
    "concept_type": "acid_base_ph_titration",
    "concept_type_label_id": "Asam-basa, pH, buffer, hidrolisis, dan titrasi",
    "template_id": "remotion.chem_acid_base_titration.v1",
    "component": "AcidBaseTitrationVideo",
    "archetype": "acid_base_titration",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Asam-basa, pH, buffer, hidrolisis, dan titrasi",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `acid_base_ph_titration`.",
    "keyIdea": "Titrasi menghubungkan penambahan larutan, perubahan pH, dan titik ekuivalen.",
    "steps": [
      {
        "id": "setup",
        "start": 90,
        "duration": 170,
        "title": "1. Siapkan larutan asam dan basa",
        "narration": "Titrasi dimulai dari larutan yang konsentrasinya ingin dianalisis."
      },
      {
        "id": "drop",
        "start": 260,
        "duration": 170,
        "title": "2. Titran ditambahkan perlahan",
        "narration": "Larutan dalam buret diteteskan sedikit demi sedikit ke erlenmeyer."
      },
      {
        "id": "neutralize",
        "start": 430,
        "duration": 170,
        "title": "3. H+ dan OH- bereaksi",
        "narration": "Ion hidrogen dan hidroksida membentuk air ketika jumlahnya setara."
      },
      {
        "id": "indicator",
        "start": 600,
        "duration": 170,
        "title": "4. Indikator berubah warna",
        "narration": "Indikator memberi tanda visual saat mendekati titik akhir titrasi."
      },
      {
        "id": "curve",
        "start": 770,
        "duration": 170,
        "title": "5. Kurva pH berubah tajam",
        "narration": "Di sekitar titik ekuivalen, pH dapat berubah sangat cepat."
      },
      {
        "id": "equivalence",
        "start": 940,
        "duration": 170,
        "title": "6. Titik ekuivalen dianalisis",
        "narration": "Titik ekuivalen menunjukkan perbandingan stoikiometri asam dan basa."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Hubungkan lab dan data",
        "narration": "Titrasi menggabungkan eksperimen, reaksi ion, dan interpretasi grafik."
      }
    ],
    "visual": {
      "acid": "HCl",
      "base": "NaOH",
      "indicator": "Fenolftalein",
      "equivalencePH": 7
    },
    "summarySequence": [
      "Setup",
      "Tetes titran",
      "Netralisasi",
      "Indikator",
      "Kurva pH",
      "Titik ekuivalen"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_030_ecosystem_interdependence",
    "row_index": 30,
    "concept_type": "ecosystem_interdependence",
    "concept_type_label_id": "Habitat, adaptasi, rantai makanan, ekosistem",
    "template_id": "remotion.sd_ecosystem_food_chain.v1",
    "component": "SDEcosystemFoodChainVideo",
    "archetype": "sd_food_chain",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Habitat, adaptasi, rantai makanan, ekosistem",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `ecosystem_interdependence`.",
    "keyIdea": "Rantai makanan memperlihatkan perpindahan energi di habitat.",
    "steps": [
      {
        "id": "habitat",
        "start": 90,
        "duration": 170,
        "title": "1. Mulai dari habitat",
        "narration": "Setiap makhluk hidup tinggal di lingkungan yang sesuai kebutuhannya."
      },
      {
        "id": "sun",
        "start": 260,
        "duration": 170,
        "title": "2. Matahari memberi energi",
        "narration": "Energi matahari membantu tumbuhan membuat makanan."
      },
      {
        "id": "producer",
        "start": 430,
        "duration": 170,
        "title": "3. Tumbuhan menjadi produsen",
        "narration": "Produsen menjadi sumber makanan bagi hewan pemakan tumbuhan."
      },
      {
        "id": "consumer",
        "start": 600,
        "duration": 170,
        "title": "4. Energi berpindah ke konsumen",
        "narration": "Konsumen memakan organisme lain dan memperoleh energi."
      },
      {
        "id": "predator",
        "start": 770,
        "duration": 170,
        "title": "5. Pemangsa menjaga keseimbangan",
        "narration": "Pemangsa membantu menjaga jumlah organisme dalam ekosistem."
      },
      {
        "id": "adaptation",
        "start": 940,
        "duration": 170,
        "title": "6. Adaptasi membantu bertahan",
        "narration": "Bentuk tubuh dan perilaku membantu makhluk hidup bertahan di habitatnya."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Rantai makanan saling terhubung",
        "narration": "Jika satu bagian berubah, bagian lain dalam rantai ikut terpengaruh."
      }
    ],
    "visual": {
      "habitat": "Sawah",
      "chain": [
        "Matahari",
        "Rumput",
        "Belalang",
        "Katak",
        "Elang"
      ],
      "adaptations": [
        "warna tubuh",
        "paruh",
        "kaki"
      ]
    },
    "summarySequence": [
      "Habitat",
      "Matahari",
      "Produsen",
      "Konsumen",
      "Predator",
      "Adaptasi"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_031_energy_light_sound_heat_electricity",
    "row_index": 31,
    "concept_type": "energy_light_sound_heat_electricity",
    "concept_type_label_id": "Energi panas, cahaya, bunyi, listrik, magnet, dan perubahannya",
    "template_id": "remotion.sd_energy_forms.v1",
    "component": "SDEnergyFormsVideo",
    "archetype": "sd_energy_forms",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_manim",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Energi panas, cahaya, bunyi, listrik, magnet, dan perubahannya",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `energy_light_sound_heat_electricity`.",
    "keyIdea": "Energi berubah bentuk saat alat bekerja.",
    "steps": [
      {
        "id": "identify",
        "start": 90,
        "duration": 170,
        "title": "1. Kenali bentuk energi",
        "narration": "Energi dapat muncul sebagai listrik, panas, cahaya, bunyi, atau magnet."
      },
      {
        "id": "electric",
        "start": 260,
        "duration": 170,
        "title": "2. Listrik mengalir ke alat",
        "narration": "Banyak alat rumah tangga memakai energi listrik."
      },
      {
        "id": "light",
        "start": 430,
        "duration": 170,
        "title": "3. Energi berubah menjadi cahaya",
        "narration": "Lampu mengubah listrik menjadi cahaya."
      },
      {
        "id": "heat",
        "start": 600,
        "duration": 170,
        "title": "4. Energi berubah menjadi panas",
        "narration": "Beberapa alat mengubah listrik atau bahan bakar menjadi panas."
      },
      {
        "id": "sound",
        "start": 770,
        "duration": 170,
        "title": "5. Energi berubah menjadi bunyi",
        "narration": "Speaker mengubah energi listrik menjadi getaran dan bunyi."
      },
      {
        "id": "magnet",
        "start": 940,
        "duration": 170,
        "title": "6. Energi dapat menimbulkan efek magnet",
        "narration": "Arus listrik dapat menghasilkan gaya magnet pada alat tertentu."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Energi tidak hilang",
        "narration": "Energi berpindah dan berubah bentuk sesuai proses yang terjadi."
      }
    ],
    "visual": {
      "forms": [
        "Listrik",
        "Panas",
        "Cahaya",
        "Bunyi",
        "Magnet"
      ],
      "examples": [
        "Lampu",
        "Kompor",
        "Speaker",
        "Kipas"
      ]
    },
    "summarySequence": [
      "Listrik",
      "Cahaya",
      "Panas",
      "Bunyi",
      "Magnet",
      "Perubahan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_034_life_structure_classification",
    "row_index": 34,
    "concept_type": "life_structure_classification",
    "concept_type_label_id": "Makhluk hidup, klasifikasi, dan struktur organisme",
    "template_id": "remotion.bio_structure_labeling.v1",
    "component": "BioStructureLabelingVideo",
    "archetype": "bio_structure_labeling",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Makhluk hidup, klasifikasi, dan struktur organisme",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `life_structure_classification`.",
    "keyIdea": "Struktur organisme membantu kita memahami fungsi dan klasifikasinya.",
    "steps": [
      {
        "id": "organism",
        "start": 90,
        "duration": 170,
        "title": "1. Amati organisme utuh",
        "narration": "Kita mulai dari bentuk organisme secara keseluruhan."
      },
      {
        "id": "root",
        "start": 260,
        "duration": 170,
        "title": "2. Akar menyerap air",
        "narration": "Akar membantu menyerap air dan mineral dari tanah."
      },
      {
        "id": "stem",
        "start": 430,
        "duration": 170,
        "title": "3. Batang mengangkut zat",
        "narration": "Batang menopang tubuh tumbuhan dan mengangkut zat."
      },
      {
        "id": "leaf",
        "start": 600,
        "duration": 170,
        "title": "4. Daun membuat makanan",
        "narration": "Daun menjadi tempat utama fotosintesis pada banyak tumbuhan."
      },
      {
        "id": "flower",
        "start": 770,
        "duration": 170,
        "title": "5. Bunga berperan dalam reproduksi",
        "narration": "Bunga membantu proses perkembangbiakan tumbuhan berbunga."
      },
      {
        "id": "classify",
        "start": 940,
        "duration": 170,
        "title": "6. Ciri membantu klasifikasi",
        "narration": "Bagian tubuh menjadi petunjuk untuk mengelompokkan organisme."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Struktur dan fungsi saling terkait",
        "narration": "Setiap bagian tubuh memiliki fungsi yang mendukung kehidupan organisme."
      }
    ],
    "visual": {
      "organism": "Tumbuhan berbunga",
      "parts": [
        "Akar",
        "Batang",
        "Daun",
        "Bunga"
      ],
      "classification": [
        "Plantae",
        "Angiospermae"
      ]
    },
    "summarySequence": [
      "Organisme",
      "Akar",
      "Batang",
      "Daun",
      "Bunga",
      "Klasifikasi"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_038_virus_structure_lifecycle_health",
    "row_index": 38,
    "concept_type": "virus_structure_lifecycle_health",
    "concept_type_label_id": "Virus, siklus replikasi, dan kesehatan",
    "template_id": "remotion.bio_virus_lifecycle.v1",
    "component": "BioVirusLifecycleVideo",
    "archetype": "virus_lifecycle",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Virus, siklus replikasi, dan kesehatan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `virus_structure_lifecycle_health`.",
    "keyIdea": "Virus memperbanyak diri dengan memanfaatkan sel inang.",
    "steps": [
      {
        "id": "entry",
        "start": 90,
        "duration": 170,
        "title": "1. Virus mendekati sel inang",
        "narration": "Virus mencari sel yang memiliki reseptor yang sesuai."
      },
      {
        "id": "attach",
        "start": 260,
        "duration": 170,
        "title": "2. Virus menempel pada reseptor",
        "narration": "Penempelan membuat virus dapat memasukkan materi genetik."
      },
      {
        "id": "inject",
        "start": 430,
        "duration": 170,
        "title": "3. Materi genetik masuk",
        "narration": "Instruksi virus masuk ke dalam sel inang."
      },
      {
        "id": "replicate",
        "start": 600,
        "duration": 170,
        "title": "4. Komponen virus digandakan",
        "narration": "Sel inang dipakai untuk membuat salinan bagian-bagian virus."
      },
      {
        "id": "assemble",
        "start": 770,
        "duration": 170,
        "title": "5. Virus baru dirakit",
        "narration": "Bagian-bagian virus disusun menjadi partikel baru."
      },
      {
        "id": "release",
        "start": 940,
        "duration": 170,
        "title": "6. Virus keluar dari sel",
        "narration": "Virus baru keluar dan dapat menginfeksi sel lain."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Pencegahan memutus siklus",
        "narration": "Perilaku sehat dan vaksin membantu mengurangi penyebaran virus."
      }
    ],
    "visual": {
      "stages": [
        "Menempel",
        "Masuk",
        "Replikasi",
        "Perakitan",
        "Keluar"
      ],
      "prevention": [
        "Vaksin",
        "Cuci tangan",
        "Masker"
      ]
    },
    "summarySequence": [
      "Menempel",
      "Masuk",
      "Replikasi",
      "Perakitan",
      "Keluar",
      "Pencegahan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_039_mutation_evolution_selection",
    "row_index": 39,
    "concept_type": "mutation_evolution_selection",
    "concept_type_label_id": "Mutasi, evolusi, seleksi alam, dan biodiversitas",
    "template_id": "remotion.bio_evolution_selection.v1",
    "component": "EvolutionSelectionVideo",
    "archetype": "evolution_selection",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Mutasi, evolusi, seleksi alam, dan biodiversitas",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `mutation_evolution_selection`.",
    "keyIdea": "Seleksi alam mengubah frekuensi sifat dalam populasi dari generasi ke generasi.",
    "steps": [
      {
        "id": "variation",
        "start": 90,
        "duration": 170,
        "title": "1. Populasi memiliki variasi",
        "narration": "Individu dalam populasi tidak semuanya sama."
      },
      {
        "id": "mutation",
        "start": 260,
        "duration": 170,
        "title": "2. Variasi dapat muncul dari mutasi",
        "narration": "Mutasi dan rekombinasi menghasilkan sifat baru."
      },
      {
        "id": "environment",
        "start": 430,
        "duration": 170,
        "title": "3. Lingkungan memberi tekanan seleksi",
        "narration": "Lingkungan tertentu membuat sebagian sifat lebih menguntungkan."
      },
      {
        "id": "survive",
        "start": 600,
        "duration": 170,
        "title": "4. Individu adaptif lebih bertahan",
        "narration": "Individu yang cocok lebih mungkin bertahan dan bereproduksi."
      },
      {
        "id": "frequency",
        "start": 770,
        "duration": 170,
        "title": "5. Frekuensi sifat berubah",
        "narration": "Sifat yang menguntungkan dapat menjadi lebih umum pada generasi berikutnya."
      },
      {
        "id": "biodiversity",
        "start": 940,
        "duration": 170,
        "title": "6. Perubahan jangka panjang membentuk biodiversitas",
        "narration": "Akumulasi perubahan dapat menghasilkan keragaman hayati."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Evolusi adalah perubahan populasi",
        "narration": "Fokus evolusi adalah perubahan sifat dalam populasi, bukan perubahan satu individu."
      }
    ],
    "visual": {
      "traits": [
        "Sifat A",
        "Sifat B",
        "Sifat C"
      ],
      "environment": "Lingkungan kering"
    },
    "summarySequence": [
      "Variasi",
      "Mutasi",
      "Seleksi",
      "Bertahan",
      "Frekuensi",
      "Evolusi"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_041_reaction_rate_collision_model",
    "row_index": 41,
    "concept_type": "reaction_rate_collision_model",
    "concept_type_label_id": "Laju reaksi dan teori tumbukan",
    "template_id": "remotion.chem_particle_reaction_rate.v1",
    "component": "ReactionCollisionEnergyVideo",
    "archetype": "reaction_collision",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Laju reaksi dan teori tumbukan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `reaction_rate_collision_model`.",
    "keyIdea": "Laju reaksi naik jika tumbukan efektif terjadi lebih sering.",
    "steps": [
      {
        "id": "particles",
        "start": 90,
        "duration": 170,
        "title": "1. Partikel bergerak acak",
        "narration": "Partikel pereaksi terus bergerak dan saling bertumbukan."
      },
      {
        "id": "collision",
        "start": 260,
        "duration": 170,
        "title": "2. Partikel bertumbukan",
        "narration": "Tumbukan menjadi awal kemungkinan terjadinya reaksi."
      },
      {
        "id": "activation",
        "start": 430,
        "duration": 170,
        "title": "3. Energi aktivasi dibutuhkan",
        "narration": "Partikel harus memiliki energi cukup untuk melewati penghalang reaksi."
      },
      {
        "id": "orientation",
        "start": 600,
        "duration": 170,
        "title": "4. Orientasi harus sesuai",
        "narration": "Selain energi, arah tumbukan juga perlu tepat."
      },
      {
        "id": "product",
        "start": 770,
        "duration": 170,
        "title": "5. Produk terbentuk",
        "narration": "Jika tumbukan efektif, ikatan berubah dan produk terbentuk."
      },
      {
        "id": "factors",
        "start": 940,
        "duration": 170,
        "title": "6. Faktor laju memengaruhi tumbukan",
        "narration": "Suhu, konsentrasi, luas permukaan, dan katalis mengubah frekuensi tumbukan efektif."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Teori tumbukan menjelaskan laju",
        "narration": "Laju reaksi dipahami dari jumlah tumbukan efektif per waktu."
      }
    ],
    "visual": {
      "reactants": [
        "A",
        "B"
      ],
      "product": "AB",
      "factors": [
        "Suhu",
        "Konsentrasi",
        "Katalis",
        "Luas permukaan"
      ]
    },
    "summarySequence": [
      "Gerak partikel",
      "Tumbukan",
      "Energi aktivasi",
      "Orientasi",
      "Produk",
      "Faktor laju"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_042_redox_electrochemistry_model",
    "row_index": 42,
    "concept_type": "redox_electrochemistry_model",
    "concept_type_label_id": "Redoks, sel volta, elektrolisis, dan korosi",
    "template_id": "remotion.chem_redox_electrochemistry.v1",
    "component": "ElectrochemicalCellVideo",
    "archetype": "electrochemical_cell",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Redoks, sel volta, elektrolisis, dan korosi",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `redox_electrochemistry_model`.",
    "keyIdea": "Redoks menghasilkan aliran elektron dan perpindahan ion yang saling menyeimbangkan.",
    "steps": [
      {
        "id": "setup",
        "start": 90,
        "duration": 170,
        "title": "1. Dua setengah sel disiapkan",
        "narration": "Sel elektrokimia terdiri dari anoda, katoda, elektrolit, dan rangkaian luar."
      },
      {
        "id": "oxidation",
        "start": 260,
        "duration": 170,
        "title": "2. Oksidasi terjadi di anoda",
        "narration": "Logam pada anoda melepaskan elektron."
      },
      {
        "id": "electron",
        "start": 430,
        "duration": 170,
        "title": "3. Elektron mengalir di kawat",
        "narration": "Elektron bergerak melalui rangkaian luar menuju katoda."
      },
      {
        "id": "reduction",
        "start": 600,
        "duration": 170,
        "title": "4. Reduksi terjadi di katoda",
        "narration": "Ion menerima elektron dan berubah menjadi zat yang lebih netral."
      },
      {
        "id": "salt",
        "start": 770,
        "duration": 170,
        "title": "5. Ion bergerak lewat jembatan garam",
        "narration": "Perpindahan ion menjaga muatan larutan tetap seimbang."
      },
      {
        "id": "voltage",
        "start": 940,
        "duration": 170,
        "title": "6. Beda potensial muncul",
        "narration": "Aliran elektron dapat dimanfaatkan sebagai energi listrik."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Redoks menghubungkan kimia dan listrik",
        "narration": "Sel elektrokimia menunjukkan reaksi kimia yang menghasilkan arus."
      }
    ],
    "visual": {
      "anode": "Zn",
      "cathode": "Cu",
      "ions": [
        "Zn²⁺",
        "Cu²⁺",
        "SO₄²⁻"
      ]
    },
    "summarySequence": [
      "Anoda",
      "Oksidasi",
      "Elektron",
      "Katoda",
      "Ion",
      "Arus listrik"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_043_organic_structure_functional_group",
    "row_index": 43,
    "concept_type": "organic_structure_functional_group",
    "concept_type_label_id": "Kimia karbon, hidrokarbon, gugus fungsi, dan polimer",
    "template_id": "remotion.chem_organic_structure.v1",
    "component": "OrganicStructureVideo",
    "archetype": "organic_structure",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Kimia karbon, hidrokarbon, gugus fungsi, dan polimer",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `organic_structure_functional_group`.",
    "keyIdea": "Gugus fungsi menentukan sifat khas senyawa organik.",
    "steps": [
      {
        "id": "carbon",
        "start": 90,
        "duration": 170,
        "title": "1. Senyawa organik punya kerangka karbon",
        "narration": "Atom karbon dapat membentuk rantai, cabang, atau cincin."
      },
      {
        "id": "chain",
        "start": 260,
        "duration": 170,
        "title": "2. Kerangka menjadi struktur utama",
        "narration": "Kerangka karbon menentukan bentuk dasar senyawa."
      },
      {
        "id": "group",
        "start": 430,
        "duration": 170,
        "title": "3. Gugus fungsi disorot",
        "narration": "Bagian tertentu dari molekul memberi sifat kimia yang khas."
      },
      {
        "id": "compare",
        "start": 600,
        "duration": 170,
        "title": "4. Beberapa gugus dibandingkan",
        "narration": "Alkohol, asam karboksilat, dan keton memiliki gugus fungsi berbeda."
      },
      {
        "id": "property",
        "start": 770,
        "duration": 170,
        "title": "5. Gugus fungsi memengaruhi sifat",
        "narration": "Titik didih, kelarutan, dan reaktivitas dipengaruhi oleh gugus fungsi."
      },
      {
        "id": "polymer",
        "start": 940,
        "duration": 170,
        "title": "6. Struktur juga menjelaskan polimer",
        "narration": "Pengulangan unit organik dapat membentuk polimer."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Struktur menjelaskan fungsi",
        "narration": "Mengenali struktur membantu memprediksi sifat dan kegunaan senyawa organik."
      }
    ],
    "visual": {
      "molecules": [
        {
          "name": "Etanol",
          "group": "-OH"
        },
        {
          "name": "Asam asetat",
          "group": "-COOH"
        },
        {
          "name": "Propanon",
          "group": "C=O"
        }
      ]
    },
    "summarySequence": [
      "Karbon",
      "Rantai",
      "Gugus fungsi",
      "Perbandingan",
      "Sifat",
      "Kegunaan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_047_body_senses_health",
    "row_index": 47,
    "concept_type": "body_senses_health",
    "concept_type_label_id": "Tubuh, pancaindra, kesehatan, dan sistem tubuh awal",
    "template_id": "remotion.sd_body_senses_health.v1",
    "component": "BodySensesHealthVideo",
    "archetype": "body_senses",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Tubuh, pancaindra, kesehatan, dan sistem tubuh awal",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `body_senses_health`.",
    "keyIdea": "Pancaindra menerima rangsang dan tubuh perlu dijaga agar tetap sehat.",
    "steps": [
      {
        "id": "body",
        "start": 90,
        "duration": 170,
        "title": "1. Kenali tubuh sendiri",
        "narration": "Tubuh memiliki bagian-bagian yang membantu kita beraktivitas."
      },
      {
        "id": "stimulus",
        "start": 260,
        "duration": 170,
        "title": "2. Lingkungan memberi rangsang",
        "narration": "Cahaya, bunyi, bau, rasa, dan sentuhan diterima oleh indra."
      },
      {
        "id": "sense",
        "start": 430,
        "duration": 170,
        "title": "3. Pancaindra menerima informasi",
        "narration": "Setiap indra memiliki fungsi yang berbeda."
      },
      {
        "id": "brain",
        "start": 600,
        "duration": 170,
        "title": "4. Informasi dikirim ke otak",
        "narration": "Otak membantu menafsirkan informasi dari indra."
      },
      {
        "id": "response",
        "start": 770,
        "duration": 170,
        "title": "5. Tubuh memberi respons",
        "narration": "Kita dapat bergerak atau mengambil keputusan setelah menerima informasi."
      },
      {
        "id": "health",
        "start": 940,
        "duration": 170,
        "title": "6. Kebiasaan sehat menjaga tubuh",
        "narration": "Makan sehat, mencuci tangan, dan tidur cukup membantu tubuh bekerja baik."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Indra dan kesehatan saling terkait",
        "narration": "Pancaindra membantu mengenal dunia, dan kesehatan membuat fungsi tubuh tetap optimal."
      }
    ],
    "visual": {
      "senses": [
        "Mata",
        "Telinga",
        "Hidung",
        "Lidah",
        "Kulit"
      ],
      "habits": [
        "Makan sehat",
        "Cuci tangan",
        "Tidur cukup"
      ]
    },
    "summarySequence": [
      "Rangsang",
      "Indra",
      "Otak",
      "Respons",
      "Kebiasaan sehat"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_048_living_things_classification_lifecycle",
    "row_index": 48,
    "concept_type": "living_things_classification_lifecycle",
    "concept_type_label_id": "Ciri makhluk hidup, klasifikasi, dan siklus hidup",
    "template_id": "remotion.sd_life_cycle_classification.v1",
    "component": "LifeCycleClassificationVideo",
    "archetype": "sd_life_cycle",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Ciri makhluk hidup, klasifikasi, dan siklus hidup",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `living_things_classification_lifecycle`.",
    "keyIdea": "Makhluk hidup bisa dikelompokkan dan mengalami tahapan hidup.",
    "steps": [
      {
        "id": "living",
        "start": 90,
        "duration": 170,
        "title": "1. Kenali ciri makhluk hidup",
        "narration": "Makhluk hidup tumbuh, bernapas, membutuhkan makanan, dan berkembang biak."
      },
      {
        "id": "group",
        "start": 260,
        "duration": 170,
        "title": "2. Kelompokkan berdasarkan ciri",
        "narration": "Hewan dan tumbuhan dapat dibedakan dari ciri tubuh dan cara hidupnya."
      },
      {
        "id": "start",
        "start": 430,
        "duration": 170,
        "title": "3. Siklus hidup dimulai",
        "narration": "Banyak hewan memulai hidup dari telur atau tahap awal tertentu."
      },
      {
        "id": "growth",
        "start": 600,
        "duration": 170,
        "title": "4. Organisme tumbuh",
        "narration": "Tubuh berubah ukuran dan bentuk seiring waktu."
      },
      {
        "id": "adult",
        "start": 770,
        "duration": 170,
        "title": "5. Individu dewasa terbentuk",
        "narration": "Tahap dewasa memungkinkan organisme berkembang biak."
      },
      {
        "id": "repeat",
        "start": 940,
        "duration": 170,
        "title": "6. Siklus berulang",
        "narration": "Siklus hidup berlanjut dari satu generasi ke generasi berikutnya."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Klasifikasi dan siklus membantu memahami kehidupan",
        "narration": "Kita memahami makhluk hidup dari ciri dan perubahan tahap hidupnya."
      }
    ],
    "visual": {
      "groups": [
        "Hewan",
        "Tumbuhan"
      ],
      "lifeCycle": [
        "Telur",
        "Larva",
        "Pupa",
        "Kupu-kupu"
      ]
    },
    "summarySequence": [
      "Ciri hidup",
      "Kelompok",
      "Tahap awal",
      "Tumbuh",
      "Dewasa",
      "Berulang"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_054_acid_base_safety_context",
    "row_index": 54,
    "concept_type": "acid_base_safety_context",
    "concept_type_label_id": "Asam-basa, zat aditif/adiktif, dan keselamatan bahan",
    "template_id": "remotion.chem_acid_base_safety.v1",
    "component": "AcidBaseSafetyVideo",
    "archetype": "acid_base_safety",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Asam-basa, zat aditif/adiktif, dan keselamatan bahan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `acid_base_safety_context`.",
    "keyIdea": "Asam dan basa harus dikenali sifatnya serta digunakan dengan aman.",
    "steps": [
      {
        "id": "examples",
        "start": 90,
        "duration": 170,
        "title": "1. Bahan sehari-hari punya sifat kimia",
        "narration": "Beberapa bahan rumah tangga bersifat asam, beberapa lainnya bersifat basa."
      },
      {
        "id": "ph",
        "start": 260,
        "duration": 170,
        "title": "2. pH membantu mengelompokkan",
        "narration": "Skala pH menunjukkan tingkat asam atau basa suatu larutan."
      },
      {
        "id": "indicator",
        "start": 430,
        "duration": 170,
        "title": "3. Indikator memberi tanda warna",
        "narration": "Indikator dapat membantu melihat sifat larutan secara visual."
      },
      {
        "id": "risk",
        "start": 600,
        "duration": 170,
        "title": "4. Risiko bahan perlu dipahami",
        "narration": "Beberapa bahan dapat mengiritasi atau berbahaya jika dipakai sembarangan."
      },
      {
        "id": "label",
        "start": 770,
        "duration": 170,
        "title": "5. Label bahan harus dibaca",
        "narration": "Label memberi petunjuk penggunaan dan peringatan bahaya."
      },
      {
        "id": "safe",
        "start": 940,
        "duration": 170,
        "title": "6. Keselamatan adalah kebiasaan",
        "narration": "Alat pelindung dan aturan dasar harus diikuti."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Konsep kimia dekat dengan kehidupan",
        "narration": "Belajar asam-basa perlu selalu disertai konteks penggunaan yang aman."
      }
    ],
    "visual": {
      "items": [
        "Cuka",
        "Jeruk",
        "Sabun",
        "Pembersih"
      ],
      "safety": [
        "Label",
        "Sarung tangan",
        "Jangan campur sembarang"
      ]
    },
    "summarySequence": [
      "Contoh",
      "pH",
      "Indikator",
      "Risiko",
      "Label",
      "Aman"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_060_chemistry_inquiry_safety_context",
    "row_index": 60,
    "concept_type": "chemistry_inquiry_safety_context",
    "concept_type_label_id": "Hakikat kimia, laboratorium, dan keselamatan",
    "template_id": "remotion.chem_lab_safety.v1",
    "component": "LabSafetyVideo",
    "archetype": "lab_safety",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Hakikat kimia, laboratorium, dan keselamatan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `chemistry_inquiry_safety_context`.",
    "keyIdea": "Eksperimen kimia harus mengikuti prosedur ilmiah dan keselamatan.",
    "steps": [
      {
        "id": "scope",
        "start": 90,
        "duration": 170,
        "title": "1. Kimia mempelajari zat",
        "narration": "Kimia mempelajari sifat, komposisi, dan perubahan zat."
      },
      {
        "id": "observe",
        "start": 260,
        "duration": 170,
        "title": "2. Mulai dengan pengamatan",
        "narration": "Eksperimen dimulai dari observasi yang jelas."
      },
      {
        "id": "tool",
        "start": 430,
        "duration": 170,
        "title": "3. Gunakan alat sesuai fungsi",
        "narration": "Alat laboratorium dipakai sesuai prosedur agar hasil aman dan akurat."
      },
      {
        "id": "record",
        "start": 600,
        "duration": 170,
        "title": "4. Catat data",
        "narration": "Pengamatan perlu dicatat agar bisa dianalisis."
      },
      {
        "id": "hazard",
        "start": 770,
        "duration": 170,
        "title": "5. Kenali simbol bahaya",
        "narration": "Simbol bahaya memberi peringatan tentang risiko bahan atau alat."
      },
      {
        "id": "safety",
        "start": 940,
        "duration": 170,
        "title": "6. Patuhi keselamatan",
        "narration": "Kacamata, sarung tangan, dan aturan lab melindungi pengguna."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Kerja ilmiah dan aman berjalan bersama",
        "narration": "Laboratorium yang baik menggabungkan rasa ingin tahu dan budaya keselamatan."
      }
    ],
    "visual": {
      "icons": [
        "Gelas kimia",
        "Api",
        "Kacamata",
        "Label bahaya"
      ],
      "workflow": [
        "Amati",
        "Catat",
        "Simpulkan"
      ]
    },
    "summarySequence": [
      "Zat",
      "Observasi",
      "Alat",
      "Data",
      "Bahaya",
      "Keselamatan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_061_matter_property_change_model",
    "row_index": 61,
    "concept_type": "matter_property_change_model",
    "concept_type_label_id": "Materi, sifat, klasifikasi, dan perubahan",
    "template_id": "remotion.chem_particle_matter.v1",
    "component": "ParticleMatterStatesVideo",
    "archetype": "particle_matter",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Materi, sifat, klasifikasi, dan perubahan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `matter_property_change_model`.",
    "keyIdea": "Sifat zat dapat dijelaskan dari susunan dan gerak partikelnya.",
    "steps": [
      {
        "id": "matter",
        "start": 90,
        "duration": 170,
        "title": "1. Materi tersusun dari partikel",
        "narration": "Zat dapat dimodelkan sebagai kumpulan partikel kecil."
      },
      {
        "id": "solid",
        "start": 260,
        "duration": 170,
        "title": "2. Padat tersusun rapat",
        "narration": "Pada zat padat, partikel tersusun rapat dan hanya bergetar di tempat."
      },
      {
        "id": "liquid",
        "start": 430,
        "duration": 170,
        "title": "3. Cair lebih mudah bergerak",
        "narration": "Pada zat cair, partikel lebih bebas bergeser."
      },
      {
        "id": "gas",
        "start": 600,
        "duration": 170,
        "title": "4. Gas bergerak berjauhan",
        "narration": "Pada gas, partikel berjauhan dan bergerak cepat."
      },
      {
        "id": "heat",
        "start": 770,
        "duration": 170,
        "title": "5. Energi mengubah gerak partikel",
        "narration": "Pemanasan membuat partikel bergerak lebih cepat."
      },
      {
        "id": "change",
        "start": 940,
        "duration": 170,
        "title": "6. Perubahan wujud terjadi",
        "narration": "Perubahan susunan dan gerak partikel menjelaskan perubahan wujud."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Model partikel menjelaskan sifat zat",
        "narration": "Dari model mikro, kita bisa memahami sifat makroskopik materi."
      }
    ],
    "visual": {
      "states": [
        "Padat",
        "Cair",
        "Gas"
      ],
      "changes": [
        "Mencair",
        "Menguap",
        "Mengembun"
      ]
    },
    "summarySequence": [
      "Partikel",
      "Padat",
      "Cair",
      "Gas",
      "Energi",
      "Perubahan wujud"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_067_observation_inquiry_skills",
    "row_index": 67,
    "concept_type": "observation_inquiry_skills",
    "concept_type_label_id": "Observasi, bertanya, mengelompokkan, dan mencatat data",
    "template_id": "remotion.sd_inquiry_observation.v1",
    "component": "InquiryObservationVideo",
    "archetype": "inquiry_observation",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Observasi, bertanya, mengelompokkan, dan mencatat data",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `observation_inquiry_skills`.",
    "keyIdea": "Inkuiri dimulai dari mengamati, bertanya, mengelompokkan, dan mencatat.",
    "steps": [
      {
        "id": "look",
        "start": 90,
        "duration": 170,
        "title": "1. Amati objek",
        "narration": "Siswa mulai dengan melihat bentuk, warna, ukuran, atau perubahan objek."
      },
      {
        "id": "ask",
        "start": 260,
        "duration": 170,
        "title": "2. Ajukan pertanyaan",
        "narration": "Pertanyaan membantu menentukan apa yang ingin diketahui."
      },
      {
        "id": "compare",
        "start": 430,
        "duration": 170,
        "title": "3. Bandingkan ciri",
        "narration": "Objek dapat dibandingkan berdasarkan ciri yang terlihat."
      },
      {
        "id": "sort",
        "start": 600,
        "duration": 170,
        "title": "4. Kelompokkan",
        "narration": "Objek dengan ciri serupa dapat dimasukkan dalam kelompok yang sama."
      },
      {
        "id": "record",
        "start": 770,
        "duration": 170,
        "title": "5. Catat hasil",
        "narration": "Hasil pengamatan perlu dicatat agar tidak hilang."
      },
      {
        "id": "conclude",
        "start": 940,
        "duration": 170,
        "title": "6. Buat kesimpulan sederhana",
        "narration": "Kesimpulan sederhana dibuat dari data yang diamati."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Ilmu dimulai dari rasa ingin tahu",
        "narration": "Keterampilan inkuiri membantu siswa belajar seperti ilmuwan kecil."
      }
    ],
    "visual": {
      "skills": [
        "Mengamati",
        "Bertanya",
        "Mengelompokkan",
        "Mencatat"
      ],
      "objects": [
        "Daun",
        "Batu",
        "Air"
      ]
    },
    "summarySequence": [
      "Amati",
      "Tanya",
      "Bandingkan",
      "Kelompokkan",
      "Catat",
      "Simpulkan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_068_matter_properties_states",
    "row_index": 68,
    "concept_type": "matter_properties_states",
    "concept_type_label_id": "Benda, sifat bahan, wujud zat, dan perubahan wujud",
    "template_id": "remotion.sd_matter_states.v1",
    "component": "SDMatterStatesVideo",
    "archetype": "sd_matter_states",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Benda, sifat bahan, wujud zat, dan perubahan wujud",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `matter_properties_states`.",
    "keyIdea": "Padat, cair, dan gas dapat dikenali dari bentuk, volume, dan contohnya.",
    "steps": [
      {
        "id": "object",
        "start": 90,
        "duration": 170,
        "title": "1. Benda punya sifat",
        "narration": "Benda dapat dibedakan dari bentuk, tekstur, dan wujudnya."
      },
      {
        "id": "solid",
        "start": 260,
        "duration": 170,
        "title": "2. Padat mempertahankan bentuk",
        "narration": "Benda padat biasanya memiliki bentuk yang tetap."
      },
      {
        "id": "liquid",
        "start": 430,
        "duration": 170,
        "title": "3. Cair mengikuti wadah",
        "narration": "Zat cair mengalir dan bentuknya mengikuti wadah."
      },
      {
        "id": "gas",
        "start": 600,
        "duration": 170,
        "title": "4. Gas mengisi ruang",
        "narration": "Gas menyebar dan mengisi ruang yang tersedia."
      },
      {
        "id": "change",
        "start": 770,
        "duration": 170,
        "title": "5. Wujud dapat berubah",
        "narration": "Pemanasan atau pendinginan dapat mengubah wujud zat."
      },
      {
        "id": "example",
        "start": 940,
        "duration": 170,
        "title": "6. Contoh sehari-hari membantu memahami",
        "narration": "Es, air, dan uap adalah contoh perubahan wujud yang mudah diamati."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Wujud zat dapat diamati",
        "narration": "Sifat wujud zat bisa dipelajari dari contoh dekat kehidupan siswa."
      }
    ],
    "visual": {
      "states": [
        "Padat",
        "Cair",
        "Gas"
      ],
      "examples": [
        "Es",
        "Air",
        "Uap"
      ]
    },
    "summarySequence": [
      "Benda",
      "Padat",
      "Cair",
      "Gas",
      "Perubahan",
      "Contoh"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_069_solar_system_day_night",
    "row_index": 69,
    "concept_type": "solar_system_day_night",
    "concept_type_label_id": "Siang-malam, Bulan-Matahari, dan tata surya awal",
    "template_id": "remotion.sd_solar_system_day_night.v1",
    "component": "SolarDayNightVideo",
    "archetype": "solar_day_night",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_manim",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Siang-malam, Bulan-Matahari, dan tata surya awal",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `solar_system_day_night`.",
    "keyIdea": "Siang dan malam terjadi karena Bumi berotasi.",
    "steps": [
      {
        "id": "sun",
        "start": 90,
        "duration": 170,
        "title": "1. Matahari memberi cahaya",
        "narration": "Matahari menjadi sumber cahaya utama bagi Bumi."
      },
      {
        "id": "earth",
        "start": 260,
        "duration": 170,
        "title": "2. Bumi berbentuk bola",
        "narration": "Karena Bumi bulat, tidak semua bagian menerima cahaya secara bersamaan."
      },
      {
        "id": "rotation",
        "start": 430,
        "duration": 170,
        "title": "3. Bumi berputar",
        "narration": "Bumi berotasi pada porosnya."
      },
      {
        "id": "day",
        "start": 600,
        "duration": 170,
        "title": "4. Sisi terang mengalami siang",
        "narration": "Bagian yang menghadap Matahari mengalami siang."
      },
      {
        "id": "night",
        "start": 770,
        "duration": 170,
        "title": "5. Sisi gelap mengalami malam",
        "narration": "Bagian yang membelakangi Matahari mengalami malam."
      },
      {
        "id": "moon",
        "start": 940,
        "duration": 170,
        "title": "6. Bulan terlihat pada waktu tertentu",
        "narration": "Bulan mengorbit Bumi dan tampak berubah posisi."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Rotasi menjelaskan pergantian hari",
        "narration": "Model ini membantu memahami pergantian siang dan malam setiap hari."
      }
    ],
    "visual": {
      "objects": [
        "Matahari",
        "Bumi",
        "Bulan"
      ],
      "focus": [
        "Rotasi",
        "Siang",
        "Malam"
      ]
    },
    "summarySequence": [
      "Matahari",
      "Bumi",
      "Rotasi",
      "Siang",
      "Malam",
      "Bulan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_070_earth_surface_resources_environment",
    "row_index": 70,
    "concept_type": "earth_surface_resources_environment",
    "concept_type_label_id": "Permukaan bumi, sumber daya alam, dan perubahan lingkungan",
    "template_id": "remotion.sd_earth_resources_environment.v1",
    "component": "EarthResourcesEnvironmentVideo",
    "archetype": "earth_resources",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Permukaan bumi, sumber daya alam, dan perubahan lingkungan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `earth_surface_resources_environment`.",
    "keyIdea": "Sumber daya alam perlu digunakan bijak agar lingkungan tetap terjaga.",
    "steps": [
      {
        "id": "surface",
        "start": 90,
        "duration": 170,
        "title": "1. Permukaan Bumi beragam",
        "narration": "Bumi memiliki daratan, perairan, hutan, gunung, dan banyak bentuk alam lain."
      },
      {
        "id": "resource",
        "start": 260,
        "duration": 170,
        "title": "2. Alam menyediakan sumber daya",
        "narration": "Air, tanah, hutan, dan mineral membantu kehidupan manusia."
      },
      {
        "id": "use",
        "start": 430,
        "duration": 170,
        "title": "3. Manusia menggunakan sumber daya",
        "narration": "Sumber daya dipakai untuk kebutuhan sehari-hari."
      },
      {
        "id": "change",
        "start": 600,
        "duration": 170,
        "title": "4. Lingkungan dapat berubah",
        "narration": "Aktivitas manusia dan peristiwa alam dapat mengubah permukaan Bumi."
      },
      {
        "id": "impact",
        "start": 770,
        "duration": 170,
        "title": "5. Perubahan membawa dampak",
        "narration": "Banjir, erosi, dan hilangnya habitat dapat terjadi jika lingkungan rusak."
      },
      {
        "id": "care",
        "start": 940,
        "duration": 170,
        "title": "6. Lingkungan perlu dijaga",
        "narration": "Penggunaan sumber daya harus dilakukan dengan bijak."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Bumi adalah rumah bersama",
        "narration": "Menjaga lingkungan berarti menjaga sumber kehidupan."
      }
    ],
    "visual": {
      "resources": [
        "Air",
        "Tanah",
        "Hutan",
        "Mineral"
      ],
      "changes": [
        "Erosi",
        "Banjir",
        "Penebangan"
      ]
    },
    "summarySequence": [
      "Permukaan",
      "Sumber daya",
      "Pemakaian",
      "Perubahan",
      "Dampak",
      "Menjaga"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_071_mixture_separation_change",
    "row_index": 71,
    "concept_type": "mixture_separation_change",
    "concept_type_label_id": "Campuran, pemisahan, larutan, dan perubahan fisika/kimia awal",
    "template_id": "remotion.sd_mixture_separation.v1",
    "component": "SDMixtureSeparationVideo",
    "archetype": "sd_mixture_separation",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Campuran, pemisahan, larutan, dan perubahan fisika/kimia awal",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `mixture_separation_change`.",
    "keyIdea": "Campuran dapat dipisahkan dengan memanfaatkan perbedaan sifat bahan.",
    "steps": [
      {
        "id": "mix",
        "start": 90,
        "duration": 170,
        "title": "1. Campuran berisi beberapa bahan",
        "narration": "Campuran terbentuk ketika dua atau lebih bahan digabungkan."
      },
      {
        "id": "observe",
        "start": 260,
        "duration": 170,
        "title": "2. Amati sifat penyusun",
        "narration": "Ukuran, kelarutan, dan wujud bahan membantu memilih cara pemisahan."
      },
      {
        "id": "sort",
        "start": 430,
        "duration": 170,
        "title": "3. Pemilahan memisahkan benda besar",
        "narration": "Bahan dengan ukuran atau bentuk berbeda dapat dipilah langsung."
      },
      {
        "id": "filter",
        "start": 600,
        "duration": 170,
        "title": "4. Penyaringan menahan partikel",
        "narration": "Saringan menahan partikel besar dan membiarkan cairan lewat."
      },
      {
        "id": "evaporate",
        "start": 770,
        "duration": 170,
        "title": "5. Penguapan menyisakan zat terlarut",
        "narration": "Jika air menguap, zat yang larut dapat tertinggal."
      },
      {
        "id": "choose",
        "start": 940,
        "duration": 170,
        "title": "6. Pilih metode yang sesuai",
        "narration": "Setiap campuran membutuhkan cara pemisahan yang sesuai sifatnya."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Pemisahan memakai sifat bahan",
        "narration": "Kita memisahkan campuran dengan mengenali perbedaan penyusunnya."
      }
    ],
    "visual": {
      "mixtures": [
        "Pasir + air",
        "Beras + batu",
        "Garam + air"
      ],
      "methods": [
        "Memilah",
        "Menyaring",
        "Menguapkan"
      ]
    },
    "summarySequence": [
      "Campuran",
      "Sifat bahan",
      "Memilah",
      "Menyaring",
      "Menguapkan",
      "Pilih metode"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_074_matter_particle_property_model",
    "row_index": 74,
    "concept_type": "matter_particle_property_model",
    "concept_type_label_id": "Zat, partikel, sifat, dan perubahan materi",
    "template_id": "remotion.chem_particle_matter.v1",
    "component": "ParticleMatterStatesVideo",
    "archetype": "particle_matter",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Zat, partikel, sifat, dan perubahan materi",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `matter_particle_property_model`.",
    "keyIdea": "Sifat zat dapat dijelaskan dari susunan dan gerak partikelnya.",
    "steps": [
      {
        "id": "matter",
        "start": 90,
        "duration": 170,
        "title": "1. Materi tersusun dari partikel",
        "narration": "Zat dapat dimodelkan sebagai kumpulan partikel kecil."
      },
      {
        "id": "solid",
        "start": 260,
        "duration": 170,
        "title": "2. Padat tersusun rapat",
        "narration": "Pada zat padat, partikel tersusun rapat dan hanya bergetar di tempat."
      },
      {
        "id": "liquid",
        "start": 430,
        "duration": 170,
        "title": "3. Cair lebih mudah bergerak",
        "narration": "Pada zat cair, partikel lebih bebas bergeser."
      },
      {
        "id": "gas",
        "start": 600,
        "duration": 170,
        "title": "4. Gas bergerak berjauhan",
        "narration": "Pada gas, partikel berjauhan dan bergerak cepat."
      },
      {
        "id": "heat",
        "start": 770,
        "duration": 170,
        "title": "5. Energi mengubah gerak partikel",
        "narration": "Pemanasan membuat partikel bergerak lebih cepat."
      },
      {
        "id": "change",
        "start": 940,
        "duration": 170,
        "title": "6. Perubahan wujud terjadi",
        "narration": "Perubahan susunan dan gerak partikel menjelaskan perubahan wujud."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Model partikel menjelaskan sifat zat",
        "narration": "Dari model mikro, kita bisa memahami sifat makroskopik materi."
      }
    ],
    "visual": {
      "states": [
        "Padat",
        "Cair",
        "Gas"
      ],
      "changes": [
        "Mencair",
        "Menguap",
        "Mengembun"
      ]
    },
    "summarySequence": [
      "Partikel",
      "Padat",
      "Cair",
      "Gas",
      "Energi",
      "Perubahan wujud"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_081_cell_structure_organelle",
    "row_index": 81,
    "concept_type": "cell_structure_organelle",
    "concept_type_label_id": "Struktur sel dan organel",
    "template_id": "remotion.bio_cell_structure.v1",
    "component": "CellStructureVideo",
    "archetype": "cell_structure",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Struktur sel dan organel",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `cell_structure_organelle`.",
    "keyIdea": "Organel bekerja sama menjaga kehidupan sel.",
    "steps": [
      {
        "id": "cell",
        "start": 90,
        "duration": 170,
        "title": "1. Sel adalah unit dasar kehidupan",
        "narration": "Semua makhluk hidup tersusun dari sel."
      },
      {
        "id": "membrane",
        "start": 260,
        "duration": 170,
        "title": "2. Membran membatasi sel",
        "narration": "Membran mengatur keluar masuknya zat."
      },
      {
        "id": "nucleus",
        "start": 430,
        "duration": 170,
        "title": "3. Inti mengatur aktivitas",
        "narration": "Inti menyimpan informasi genetik dan mengarahkan aktivitas sel."
      },
      {
        "id": "mitochondria",
        "start": 600,
        "duration": 170,
        "title": "4. Mitokondria menghasilkan energi",
        "narration": "Mitokondria membantu menghasilkan energi untuk kerja sel."
      },
      {
        "id": "chloroplast",
        "start": 770,
        "duration": 170,
        "title": "5. Kloroplas melakukan fotosintesis",
        "narration": "Pada sel tumbuhan, kloroplas membantu menangkap energi cahaya."
      },
      {
        "id": "compare",
        "start": 940,
        "duration": 170,
        "title": "6. Sel hewan dan tumbuhan dibandingkan",
        "narration": "Keduanya memiliki persamaan dan perbedaan organel."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Organel bekerja sebagai sistem",
        "narration": "Setiap organel memiliki fungsi yang mendukung kehidupan sel."
      }
    ],
    "visual": {
      "organelles": [
        "Membran",
        "Inti",
        "Sitoplasma",
        "Mitokondria",
        "Kloroplas"
      ],
      "cellTypes": [
        "Sel hewan",
        "Sel tumbuhan"
      ]
    },
    "summarySequence": [
      "Sel",
      "Membran",
      "Inti",
      "Mitokondria",
      "Kloroplas",
      "Perbandingan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_082_membrane_transport_model",
    "row_index": 82,
    "concept_type": "membrane_transport_model",
    "concept_type_label_id": "Transpor membran, osmosis, dan difusi",
    "template_id": "remotion.bio_membrane_transport.v1",
    "component": "MembraneTransportVideo",
    "archetype": "membrane_transport",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Transpor membran, osmosis, dan difusi",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `membrane_transport_model`.",
    "keyIdea": "Membran sel selektif: tidak semua zat lewat dengan cara yang sama.",
    "steps": [
      {
        "id": "membrane",
        "start": 90,
        "duration": 170,
        "title": "1. Membran membatasi sel",
        "narration": "Membran sel memisahkan bagian dalam dan luar sel."
      },
      {
        "id": "gradient",
        "start": 260,
        "duration": 170,
        "title": "2. Ada perbedaan konsentrasi",
        "narration": "Zat cenderung bergerak dari konsentrasi tinggi ke rendah."
      },
      {
        "id": "diffusion",
        "start": 430,
        "duration": 170,
        "title": "3. Difusi memindahkan partikel kecil",
        "narration": "Partikel tertentu dapat berdifusi melewati membran."
      },
      {
        "id": "osmosis",
        "start": 600,
        "duration": 170,
        "title": "4. Osmosis memindahkan air",
        "narration": "Air bergerak melalui membran semipermeabel menuju daerah yang lebih pekat."
      },
      {
        "id": "channel",
        "start": 770,
        "duration": 170,
        "title": "5. Protein kanal membantu transport",
        "narration": "Beberapa zat membutuhkan protein khusus untuk melewati membran."
      },
      {
        "id": "active",
        "start": 940,
        "duration": 170,
        "title": "6. Transpor aktif memakai energi",
        "narration": "Transpor aktif dapat memindahkan zat melawan gradien konsentrasi."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Transport menjaga keseimbangan sel",
        "narration": "Perpindahan zat membantu sel mempertahankan kondisi internal."
      }
    ],
    "visual": {
      "mechanisms": [
        "Difusi",
        "Osmosis",
        "Transpor aktif"
      ],
      "particles": [
        "Air",
        "Ion",
        "Glukosa"
      ]
    },
    "summarySequence": [
      "Membran",
      "Gradien",
      "Difusi",
      "Osmosis",
      "Kanal",
      "Energi"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_083_cell_division_cycle",
    "row_index": 83,
    "concept_type": "cell_division_cycle",
    "concept_type_label_id": "Pembelahan sel mitosis dan meiosis",
    "template_id": "remotion.bio_cell_division.v1",
    "component": "CellDivisionVideo",
    "archetype": "cell_division",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Pembelahan sel mitosis dan meiosis",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `cell_division_cycle`.",
    "keyIdea": "Pembelahan sel menggandakan dan membagi materi genetik secara teratur.",
    "steps": [
      {
        "id": "parent",
        "start": 90,
        "duration": 170,
        "title": "1. Mulai dari sel induk",
        "narration": "Pembelahan dimulai dari satu sel induk."
      },
      {
        "id": "duplicate",
        "start": 260,
        "duration": 170,
        "title": "2. Kromosom digandakan",
        "narration": "Materi genetik disalin agar dapat dibagi ke sel baru."
      },
      {
        "id": "align",
        "start": 430,
        "duration": 170,
        "title": "3. Kromosom berjajar",
        "narration": "Kromosom tersusun di tengah sel sebelum dipisahkan."
      },
      {
        "id": "separate",
        "start": 600,
        "duration": 170,
        "title": "4. Kromosom dipisahkan",
        "narration": "Salinan kromosom bergerak ke sisi berlawanan."
      },
      {
        "id": "divide",
        "start": 770,
        "duration": 170,
        "title": "5. Sel membelah",
        "narration": "Membran sel membagi sitoplasma menjadi dua bagian."
      },
      {
        "id": "compare",
        "start": 940,
        "duration": 170,
        "title": "6. Mitosis dan meiosis dibandingkan",
        "narration": "Mitosis menghasilkan sel identik, meiosis menghasilkan sel reproduksi."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Pembelahan mendukung kehidupan",
        "narration": "Pembelahan sel penting untuk pertumbuhan, perbaikan, dan reproduksi."
      }
    ],
    "visual": {
      "mitosis": [
        "Profase",
        "Metafase",
        "Anafase",
        "Telofase"
      ],
      "meiosis": [
        "Meiosis I",
        "Meiosis II"
      ]
    },
    "summarySequence": [
      "Sel induk",
      "Duplikasi",
      "Berjajar",
      "Berpisah",
      "Sel anak",
      "Fungsi"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_084_enzyme_metabolism_process",
    "row_index": 84,
    "concept_type": "enzyme_metabolism_process",
    "concept_type_label_id": "Enzim dan metabolisme sel",
    "template_id": "remotion.bio_enzyme_metabolism.v1",
    "component": "EnzymeMetabolismVideo",
    "archetype": "enzyme_metabolism",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Enzim dan metabolisme sel",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `enzyme_metabolism_process`.",
    "keyIdea": "Enzim mempercepat reaksi dengan mengikat substrat secara spesifik.",
    "steps": [
      {
        "id": "enzyme",
        "start": 90,
        "duration": 170,
        "title": "1. Enzim adalah biokatalis",
        "narration": "Enzim mempercepat reaksi metabolisme tanpa habis digunakan."
      },
      {
        "id": "substrate",
        "start": 260,
        "duration": 170,
        "title": "2. Substrat mendekati sisi aktif",
        "narration": "Substrat harus sesuai dengan bentuk sisi aktif enzim."
      },
      {
        "id": "complex",
        "start": 430,
        "duration": 170,
        "title": "3. Kompleks enzim-substrat terbentuk",
        "narration": "Enzim dan substrat berikatan sementara."
      },
      {
        "id": "reaction",
        "start": 600,
        "duration": 170,
        "title": "4. Reaksi berlangsung lebih mudah",
        "narration": "Enzim menurunkan energi aktivasi sehingga reaksi lebih cepat."
      },
      {
        "id": "product",
        "start": 770,
        "duration": 170,
        "title": "5. Produk dilepaskan",
        "narration": "Setelah reaksi selesai, produk keluar dari sisi aktif."
      },
      {
        "id": "factor",
        "start": 940,
        "duration": 170,
        "title": "6. Faktor lingkungan memengaruhi enzim",
        "narration": "Suhu, pH, dan konsentrasi dapat mengubah aktivitas enzim."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Spesifisitas menentukan kerja enzim",
        "narration": "Enzim bekerja efektif jika kondisi dan substratnya sesuai."
      }
    ],
    "visual": {
      "stages": [
        "Substrat",
        "Kompleks enzim-substrat",
        "Produk"
      ],
      "factors": [
        "Suhu",
        "pH",
        "Konsentrasi"
      ]
    },
    "summarySequence": [
      "Enzim",
      "Substrat",
      "Kompleks",
      "Reaksi",
      "Produk",
      "Faktor"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_085_photosynthesis_respiration_process",
    "row_index": 85,
    "concept_type": "photosynthesis_respiration_process",
    "concept_type_label_id": "Fotosintesis dan respirasi sel",
    "template_id": "remotion.bio_energy_process.v1",
    "component": "PhotosynthesisRespirationVideo",
    "archetype": "bio_energy_process",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Fotosintesis dan respirasi sel",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `photosynthesis_respiration_process`.",
    "keyIdea": "Fotosintesis menyimpan energi, respirasi melepaskan energi.",
    "steps": [
      {
        "id": "plant",
        "start": 90,
        "duration": 170,
        "title": "1. Tumbuhan menangkap cahaya",
        "narration": "Tumbuhan memakai cahaya matahari untuk membuat makanan."
      },
      {
        "id": "photo_input",
        "start": 260,
        "duration": 170,
        "title": "2. Fotosintesis memakai CO₂ dan air",
        "narration": "Karbon dioksida dan air menjadi bahan awal fotosintesis."
      },
      {
        "id": "photo_output",
        "start": 430,
        "duration": 170,
        "title": "3. Glukosa dan oksigen terbentuk",
        "narration": "Fotosintesis menghasilkan glukosa dan oksigen."
      },
      {
        "id": "cell",
        "start": 600,
        "duration": 170,
        "title": "4. Sel memakai glukosa",
        "narration": "Makhluk hidup menggunakan glukosa sebagai sumber energi."
      },
      {
        "id": "respiration",
        "start": 770,
        "duration": 170,
        "title": "5. Respirasi melepaskan energi",
        "narration": "Respirasi mengubah glukosa dan oksigen menjadi energi."
      },
      {
        "id": "cycle",
        "start": 940,
        "duration": 170,
        "title": "6. Dua proses saling terkait",
        "narration": "Produk fotosintesis dapat menjadi bahan respirasi."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Energi mengalir dalam kehidupan",
        "narration": "Fotosintesis dan respirasi menghubungkan cahaya, makanan, dan energi sel."
      }
    ],
    "visual": {
      "photosynthesis": [
        "CO₂",
        "H₂O",
        "Cahaya",
        "Glukosa",
        "O₂"
      ],
      "respiration": [
        "Glukosa",
        "O₂",
        "CO₂",
        "H₂O",
        "Energi"
      ]
    },
    "summarySequence": [
      "Cahaya",
      "CO₂ + H₂O",
      "Glukosa + O₂",
      "Respirasi",
      "Energi",
      "Siklus"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_086_genetic_information_expression",
    "row_index": 86,
    "concept_type": "genetic_information_expression",
    "concept_type_label_id": "DNA, gen, kromosom, dan sintesis protein",
    "template_id": "remotion.bio_genetic_expression.v1",
    "component": "GeneticExpressionVideo",
    "archetype": "genetic_expression",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "DNA, gen, kromosom, dan sintesis protein",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `genetic_information_expression`.",
    "keyIdea": "Informasi DNA dibaca menjadi RNA lalu diterjemahkan menjadi protein.",
    "steps": [
      {
        "id": "dna",
        "start": 90,
        "duration": 170,
        "title": "1. DNA menyimpan instruksi",
        "narration": "Informasi genetik disimpan dalam urutan basa DNA."
      },
      {
        "id": "open",
        "start": 260,
        "duration": 170,
        "title": "2. DNA terbuka sementara",
        "narration": "Bagian gen tertentu dibuka agar dapat disalin."
      },
      {
        "id": "transcription",
        "start": 430,
        "duration": 170,
        "title": "3. Transkripsi menghasilkan mRNA",
        "narration": "Informasi DNA disalin menjadi RNA pembawa pesan."
      },
      {
        "id": "ribosome",
        "start": 600,
        "duration": 170,
        "title": "4. mRNA menuju ribosom",
        "narration": "Ribosom membaca kode pada mRNA."
      },
      {
        "id": "translation",
        "start": 770,
        "duration": 170,
        "title": "5. Asam amino dirangkai",
        "narration": "Kodon diterjemahkan menjadi urutan asam amino."
      },
      {
        "id": "protein",
        "start": 940,
        "duration": 170,
        "title": "6. Protein terbentuk",
        "narration": "Rantai asam amino melipat menjadi protein yang berfungsi."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Gen diekspresikan lewat protein",
        "narration": "Ekspresi gen menghubungkan informasi DNA dengan fungsi sel."
      }
    ],
    "visual": {
      "stages": [
        "DNA",
        "mRNA",
        "Ribosom",
        "Protein"
      ],
      "keywords": [
        "Transkripsi",
        "Translasi",
        "Kodon"
      ]
    },
    "summarySequence": [
      "DNA",
      "Transkripsi",
      "mRNA",
      "Ribosom",
      "Translasi",
      "Protein"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_088_growth_development_timeline",
    "row_index": 88,
    "concept_type": "growth_development_timeline",
    "concept_type_label_id": "Pertumbuhan dan perkembangan organisme",
    "template_id": "remotion.bio_growth_timeline.v1",
    "component": "GrowthTimelineVideo",
    "archetype": "growth_timeline",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Pertumbuhan dan perkembangan organisme",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `growth_development_timeline`.",
    "keyIdea": "Pertumbuhan dan perkembangan berlangsung bertahap dan dipengaruhi banyak faktor.",
    "steps": [
      {
        "id": "start",
        "start": 90,
        "duration": 170,
        "title": "1. Organisme memulai tahap hidup",
        "narration": "Setiap organisme memiliki tahap awal perkembangan."
      },
      {
        "id": "growth",
        "start": 260,
        "duration": 170,
        "title": "2. Ukuran bertambah",
        "narration": "Pertumbuhan berkaitan dengan peningkatan ukuran atau massa."
      },
      {
        "id": "development",
        "start": 430,
        "duration": 170,
        "title": "3. Fungsi menjadi matang",
        "narration": "Perkembangan berkaitan dengan perubahan bentuk dan fungsi."
      },
      {
        "id": "timeline",
        "start": 600,
        "duration": 170,
        "title": "4. Tahap disusun dalam urutan waktu",
        "narration": "Timeline membantu melihat perubahan dari satu tahap ke tahap berikutnya."
      },
      {
        "id": "factors",
        "start": 770,
        "duration": 170,
        "title": "5. Faktor memengaruhi proses",
        "narration": "Genetik, nutrisi, hormon, dan lingkungan memengaruhi pertumbuhan."
      },
      {
        "id": "compare",
        "start": 940,
        "duration": 170,
        "title": "6. Kecepatan bisa berbeda",
        "narration": "Setiap organisme dapat memiliki pola pertumbuhan yang berbeda."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Pertumbuhan tidak hanya soal besar",
        "narration": "Perkembangan fungsi sama pentingnya dengan pertambahan ukuran."
      }
    ],
    "visual": {
      "timeline": [
        "Bayi",
        "Anak",
        "Remaja",
        "Dewasa"
      ],
      "factors": [
        "Genetik",
        "Nutrisi",
        "Hormon",
        "Lingkungan"
      ]
    },
    "summarySequence": [
      "Tahap awal",
      "Bertambah besar",
      "Matang fungsi",
      "Timeline",
      "Faktor",
      "Perbedaan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_089_materials_nanotech_environment",
    "row_index": 89,
    "concept_type": "materials_nanotech_environment",
    "concept_type_label_id": "Material, nanoteknologi, dan kimia lingkungan",
    "template_id": "remotion.chem_material_environment.v1",
    "component": "MaterialsEnvironmentVideo",
    "archetype": "material_environment",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Material, nanoteknologi, dan kimia lingkungan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `materials_nanotech_environment`.",
    "keyIdea": "Material modern bermanfaat, tetapi dampaknya terhadap lingkungan harus dinilai.",
    "steps": [
      {
        "id": "material",
        "start": 90,
        "duration": 170,
        "title": "1. Material punya struktur berbeda",
        "narration": "Sifat material ditentukan oleh struktur dan komposisinya."
      },
      {
        "id": "nano",
        "start": 260,
        "duration": 170,
        "title": "2. Skala nano mengubah sifat",
        "narration": "Pada skala sangat kecil, sifat material bisa berubah signifikan."
      },
      {
        "id": "application",
        "start": 430,
        "duration": 170,
        "title": "3. Aplikasi teknologi muncul",
        "narration": "Material modern digunakan pada sensor, medis, pelapis, dan banyak bidang lain."
      },
      {
        "id": "benefit",
        "start": 600,
        "duration": 170,
        "title": "4. Manfaat perlu dibandingkan",
        "narration": "Manfaat material dilihat dari fungsi, efisiensi, dan ketahanannya."
      },
      {
        "id": "impact",
        "start": 770,
        "duration": 170,
        "title": "5. Dampak lingkungan diperhitungkan",
        "narration": "Limbah, toksisitas, dan proses produksi perlu diperhatikan."
      },
      {
        "id": "sustain",
        "start": 940,
        "duration": 170,
        "title": "6. Keberlanjutan menjadi tujuan",
        "narration": "Daur ulang dan desain ramah lingkungan penting dalam pengembangan material."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Material harus dinilai menyeluruh",
        "narration": "Teknologi material perlu menyeimbangkan fungsi dan tanggung jawab lingkungan."
      }
    ],
    "visual": {
      "materials": [
        "Polimer",
        "Komposit",
        "Nanopartikel"
      ],
      "applications": [
        "Sensor",
        "Medis",
        "Pelapis"
      ],
      "impacts": [
        "Limbah",
        "Daur ulang",
        "Toksisitas"
      ]
    },
    "summarySequence": [
      "Struktur",
      "Nano",
      "Aplikasi",
      "Manfaat",
      "Dampak",
      "Keberlanjutan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_096_earth_weather_water_cycle",
    "row_index": 96,
    "concept_type": "earth_weather_water_cycle",
    "concept_type_label_id": "Cuaca, musim, daur air, dan peristiwa alam",
    "template_id": "remotion.sd_weather_water_cycle.v1",
    "component": "WeatherWaterCycleVideo",
    "archetype": "water_cycle",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Cuaca, musim, daur air, dan peristiwa alam",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `earth_weather_water_cycle`.",
    "keyIdea": "Daur air menjelaskan hubungan panas matahari, awan, hujan, dan aliran air.",
    "steps": [
      {
        "id": "sun",
        "start": 90,
        "duration": 170,
        "title": "1. Matahari memanaskan air",
        "narration": "Panas matahari membuat air di permukaan menguap."
      },
      {
        "id": "evaporation",
        "start": 260,
        "duration": 170,
        "title": "2. Uap air naik",
        "narration": "Air berubah menjadi uap dan naik ke udara."
      },
      {
        "id": "condensation",
        "start": 430,
        "duration": 170,
        "title": "3. Awan terbentuk",
        "narration": "Uap air mendingin dan berkumpul menjadi awan."
      },
      {
        "id": "rain",
        "start": 600,
        "duration": 170,
        "title": "4. Hujan turun",
        "narration": "Saat awan jenuh, air jatuh kembali sebagai hujan."
      },
      {
        "id": "runoff",
        "start": 770,
        "duration": 170,
        "title": "5. Air mengalir kembali",
        "narration": "Air mengalir ke sungai, danau, atau laut."
      },
      {
        "id": "weather",
        "start": 940,
        "duration": 170,
        "title": "6. Cuaca bisa berubah",
        "narration": "Daur air berkaitan dengan cuaca seperti cerah, berawan, dan hujan."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Air terus berputar",
        "narration": "Daur air menunjukkan bahwa air berpindah tempat dan berubah wujud terus-menerus."
      }
    ],
    "visual": {
      "cycle": [
        "Penguapan",
        "Kondensasi",
        "Hujan",
        "Aliran"
      ],
      "weather": [
        "Cerah",
        "Berawan",
        "Hujan",
        "Berangin"
      ]
    },
    "summarySequence": [
      "Matahari",
      "Penguapan",
      "Awan",
      "Hujan",
      "Aliran",
      "Cuaca"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_101_mixture_separation_lab_model",
    "row_index": 101,
    "concept_type": "mixture_separation_lab_model",
    "concept_type_label_id": "Campuran dan pemisahan sederhana",
    "template_id": "remotion.chem_lab_separation.v1",
    "component": "LabSeparationVideo",
    "archetype": "lab_separation",
    "domain": "chemistry",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Campuran dan pemisahan sederhana",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `mixture_separation_lab_model`.",
    "keyIdea": "Pemisahan campuran dipilih berdasarkan sifat fisik penyusunnya.",
    "steps": [
      {
        "id": "mixture",
        "start": 90,
        "duration": 170,
        "title": "1. Campuran dianalisis",
        "narration": "Campuran memiliki beberapa komponen dengan sifat berbeda."
      },
      {
        "id": "property",
        "start": 260,
        "duration": 170,
        "title": "2. Sifat pembeda dicari",
        "narration": "Ukuran partikel, titik didih, dan kelarutan bisa menjadi dasar pemisahan."
      },
      {
        "id": "filtration",
        "start": 430,
        "duration": 170,
        "title": "3. Filtrasi memisahkan partikel",
        "narration": "Saringan menahan padatan dan membiarkan cairan lewat."
      },
      {
        "id": "distillation",
        "start": 600,
        "duration": 170,
        "title": "4. Distilasi memakai titik didih",
        "narration": "Komponen dipisahkan karena menguap dan mengembun pada suhu berbeda."
      },
      {
        "id": "chromatography",
        "start": 770,
        "duration": 170,
        "title": "5. Kromatografi memisahkan zat terlarut",
        "narration": "Komponen bergerak berbeda pada fase diam dan fase gerak."
      },
      {
        "id": "choose",
        "start": 940,
        "duration": 170,
        "title": "6. Metode dipilih sesuai campuran",
        "narration": "Tidak semua campuran cocok dipisahkan dengan metode yang sama."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Sifat fisik menjadi kunci",
        "narration": "Pemisahan campuran adalah penerapan langsung dari sifat fisik zat."
      }
    ],
    "visual": {
      "methods": [
        "Filtrasi",
        "Distilasi",
        "Kromatografi"
      ],
      "mixtures": [
        "Pasir + air",
        "Alkohol + air",
        "Tinta"
      ]
    },
    "summarySequence": [
      "Campuran",
      "Sifat",
      "Filtrasi",
      "Distilasi",
      "Kromatografi",
      "Pilihan metode"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_103_immune_response_interaction",
    "row_index": 103,
    "concept_type": "immune_response_interaction",
    "concept_type_label_id": "Sistem imun dan interaksi pertahanan tubuh",
    "template_id": "remotion.bio_immune_response.v1",
    "component": "ImmuneResponseVideo",
    "archetype": "immune_response",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Sistem imun dan interaksi pertahanan tubuh",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `immune_response_interaction`.",
    "keyIdea": "Sistem imun mengenali patogen, menyerang, lalu menyimpan memori.",
    "steps": [
      {
        "id": "virus-entry",
        "start": 90,
        "duration": 170,
        "title": "1. Virus masuk ke tubuh",
        "narration": "Virus memasuki tubuh dan mulai mencari sel yang bisa diinfeksi."
      },
      {
        "id": "infected-cell",
        "start": 260,
        "duration": 170,
        "title": "2. Sel memberi sinyal bahaya",
        "narration": "Sel yang terinfeksi mengirim sinyal kimia agar sistem imun datang."
      },
      {
        "id": "macrophage",
        "start": 430,
        "duration": 170,
        "title": "3. Makrofag menelan patogen",
        "narration": "Makrofag bekerja seperti petugas kebersihan tubuh yang menelan benda asing."
      },
      {
        "id": "antigen",
        "start": 600,
        "duration": 170,
        "title": "4. Antigen dipresentasikan",
        "narration": "Potongan virus ditampilkan sebagai antigen agar sel imun lain mengenali musuh."
      },
      {
        "id": "activation",
        "start": 770,
        "duration": 170,
        "title": "5. Helper T cell mengaktifkan B cell",
        "narration": "Helper T cell memberi instruksi agar B cell memproduksi antibodi."
      },
      {
        "id": "antibody",
        "start": 940,
        "duration": 170,
        "title": "6. Antibodi menetralkan virus",
        "narration": "Antibodi menempel pada virus sehingga virus lebih mudah dihancurkan."
      },
      {
        "id": "memory",
        "start": 1110,
        "duration": 170,
        "title": "7. Memory cell tetap berjaga",
        "narration": "Sebagian sel berubah menjadi memory cell agar respons berikutnya lebih cepat."
      }
    ],
    "visual": {
      "actors": [
        "Virus",
        "Sel tubuh",
        "Makrofag",
        "Helper T cell",
        "B cell",
        "Antibodi",
        "Memory cell"
      ]
    },
    "summarySequence": [
      "Virus masuk",
      "Sinyal bahaya",
      "Makrofag",
      "Antigen",
      "B cell",
      "Antibodi",
      "Memori"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_104_homeostasis_feedback_model",
    "row_index": 104,
    "concept_type": "homeostasis_feedback_model",
    "concept_type_label_id": "Homeostasis dan umpan balik biologis",
    "template_id": "remotion.bio_homeostasis_feedback.v1",
    "component": "HomeostasisFeedbackVideo",
    "archetype": "homeostasis_feedback",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Homeostasis dan umpan balik biologis",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `homeostasis_feedback_model`.",
    "keyIdea": "Homeostasis menjaga kondisi internal melalui loop umpan balik.",
    "steps": [
      {
        "id": "setpoint",
        "start": 90,
        "duration": 170,
        "title": "1. Tubuh memiliki set point",
        "narration": "Kondisi internal dijaga di sekitar nilai normal."
      },
      {
        "id": "stimulus",
        "start": 260,
        "duration": 170,
        "title": "2. Perubahan terdeteksi",
        "narration": "Stimulus membuat kondisi menyimpang dari set point."
      },
      {
        "id": "receptor",
        "start": 430,
        "duration": 170,
        "title": "3. Reseptor membaca perubahan",
        "narration": "Reseptor mengirim informasi ke pusat kontrol."
      },
      {
        "id": "control",
        "start": 600,
        "duration": 170,
        "title": "4. Pusat kontrol memproses sinyal",
        "narration": "Pusat kontrol menentukan respons yang diperlukan."
      },
      {
        "id": "effector",
        "start": 770,
        "duration": 170,
        "title": "5. Efektor bekerja",
        "narration": "Efektor melakukan tindakan untuk mengurangi penyimpangan."
      },
      {
        "id": "feedback",
        "start": 940,
        "duration": 170,
        "title": "6. Umpan balik menstabilkan kondisi",
        "narration": "Respons mengembalikan kondisi mendekati set point."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Loop menjaga kestabilan",
        "narration": "Homeostasis terjadi karena deteksi, kontrol, dan respons yang terus berulang."
      }
    ],
    "visual": {
      "loop": [
        "Stimulus",
        "Reseptor",
        "Pusat kontrol",
        "Efektor",
        "Respon"
      ],
      "examples": [
        "Suhu tubuh",
        "Glukosa darah"
      ]
    },
    "summarySequence": [
      "Set point",
      "Stimulus",
      "Reseptor",
      "Kontrol",
      "Efektor",
      "Stabil"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_105_disease_disorder_context",
    "row_index": 105,
    "concept_type": "disease_disorder_context",
    "concept_type_label_id": "Gangguan sistem organ dan konteks kesehatan",
    "template_id": "remotion.bio_health_disorder.v1",
    "component": "HealthDisorderVideo",
    "archetype": "health_disorder",
    "domain": "biology",
    "media_engine_family": "remotion_svg",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Gangguan sistem organ dan konteks kesehatan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `disease_disorder_context`.",
    "keyIdea": "Gangguan sistem organ dipahami melalui sistem yang terkena, gejala, dan pencegahan.",
    "steps": [
      {
        "id": "system",
        "start": 90,
        "duration": 170,
        "title": "1. Setiap gangguan terkait sistem organ",
        "narration": "Gangguan kesehatan biasanya memengaruhi sistem tubuh tertentu."
      },
      {
        "id": "case1",
        "start": 260,
        "duration": 170,
        "title": "2. Contoh gangguan dikenali",
        "narration": "Kasus seperti asma, anemia, atau diabetes punya ciri berbeda."
      },
      {
        "id": "symptom",
        "start": 430,
        "duration": 170,
        "title": "3. Gejala menjadi petunjuk",
        "narration": "Gejala membantu mengenali kemungkinan masalah pada tubuh."
      },
      {
        "id": "cause",
        "start": 600,
        "duration": 170,
        "title": "4. Penyebab dianalisis",
        "narration": "Penyebab dapat berasal dari infeksi, gaya hidup, genetik, atau lingkungan."
      },
      {
        "id": "prevention",
        "start": 770,
        "duration": 170,
        "title": "5. Pencegahan ditekankan",
        "narration": "Kebiasaan sehat dapat menurunkan risiko beberapa gangguan."
      },
      {
        "id": "care",
        "start": 940,
        "duration": 170,
        "title": "6. Penanganan harus tepat",
        "narration": "Masalah kesehatan perlu ditangani sesuai penyebab dan kondisinya."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Konteks kesehatan perlu utuh",
        "narration": "Belajar gangguan tubuh harus menghubungkan sistem, gejala, sebab, dan pencegahan."
      }
    ],
    "visual": {
      "cases": [
        "Asma",
        "Anemia",
        "Diabetes"
      ],
      "columns": [
        "Sistem",
        "Gejala",
        "Pencegahan"
      ]
    },
    "summarySequence": [
      "Sistem",
      "Kasus",
      "Gejala",
      "Sebab",
      "Pencegahan",
      "Penanganan"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  },
  {
    "id": "remotion_v2_107_plant_animal_structure_function",
    "row_index": 107,
    "concept_type": "plant_animal_structure_function",
    "concept_type_label_id": "Struktur dan fungsi bagian tubuh tumbuhan/hewan",
    "template_id": "remotion.sd_structure_function.v1",
    "component": "StructureFunctionVideo",
    "archetype": "structure_function",
    "domain": "sd_science",
    "media_engine_family": "remotion_or_rive",
    "language": "id",
    "fps": 30,
    "width": 1280,
    "height": 720,
    "durationInFrames": 1350,
    "title": "Struktur dan fungsi bagian tubuh tumbuhan/hewan",
    "subtitle": "Video penjelasan berbasis mekanisme untuk concept type `plant_animal_structure_function`.",
    "keyIdea": "Bentuk bagian tubuh terkait dengan fungsi yang membantu makhluk hidup bertahan.",
    "steps": [
      {
        "id": "compare",
        "start": 90,
        "duration": 170,
        "title": "1. Bandingkan tumbuhan dan hewan",
        "narration": "Tumbuhan dan hewan memiliki bagian tubuh dengan bentuk yang berbeda."
      },
      {
        "id": "plant-root",
        "start": 260,
        "duration": 170,
        "title": "2. Akar menyerap air",
        "narration": "Akar tumbuhan membantu mengambil air dari tanah."
      },
      {
        "id": "plant-leaf",
        "start": 430,
        "duration": 170,
        "title": "3. Daun membuat makanan",
        "narration": "Daun membantu tumbuhan membuat makanan dengan cahaya."
      },
      {
        "id": "animal-beak",
        "start": 600,
        "duration": 170,
        "title": "4. Bagian tubuh hewan membantu makan",
        "narration": "Paruh atau mulut hewan sesuai dengan jenis makanannya."
      },
      {
        "id": "animal-move",
        "start": 770,
        "duration": 170,
        "title": "5. Kaki atau sirip membantu bergerak",
        "narration": "Struktur gerak membantu hewan berpindah tempat."
      },
      {
        "id": "adapt",
        "start": 940,
        "duration": 170,
        "title": "6. Struktur membantu adaptasi",
        "narration": "Bentuk tubuh mendukung cara makhluk hidup bertahan."
      },
      {
        "id": "summary",
        "start": 1110,
        "duration": 170,
        "title": "7. Struktur dan fungsi saling menjelaskan",
        "narration": "Kita memahami makhluk hidup dengan mengaitkan bagian tubuh dan fungsinya."
      }
    ],
    "visual": {
      "plantParts": [
        "Akar",
        "Batang",
        "Daun",
        "Bunga"
      ],
      "animalParts": [
        "Paruh",
        "Sirip",
        "Kaki",
        "Bulu"
      ]
    },
    "summarySequence": [
      "Tumbuhan",
      "Akar",
      "Daun",
      "Hewan",
      "Gerak",
      "Adaptasi"
    ],
    "qualityIntent": {
      "mode": "video_explainer",
      "minimumEvents": [
        "title_card",
        "context_objects",
        "main_motion",
        "interaction",
        "state_change",
        "active_narration",
        "final_summary"
      ],
      "layoutSafeZones": {
        "mainVisual": "x=40..900,y=120..520",
        "stepPanel": "x=56..820,y=535..680",
        "keyIdea": "x=920..1230,y=44..190"
      }
    }
  }
] as RemotionConceptSpec[];

const componentMap: Record<string, any> = {
  EcosystemNetworkVideo: Templates.EcosystemNetworkVideo,
  OrganSystemFlowVideo: Templates.OrganSystemFlowVideo,
  EarthSpaceSystemVideo: Templates.EarthSpaceSystemVideo,
  ChemBondingMoleculeVideo: Templates.ChemBondingMoleculeVideo,
  HumanBodyFlowVideo: Templates.HumanBodyFlowVideo,
  TaxonomyBiodiversityVideo: Templates.TaxonomyBiodiversityVideo,
  BiotechProcessVideo: Templates.BiotechProcessVideo,
  AtomicPeriodicVideo: Templates.AtomicPeriodicVideo,
  AcidBaseTitrationVideo: Templates.AcidBaseTitrationVideo,
  SDEcosystemFoodChainVideo: Templates.SDEcosystemFoodChainVideo,
  SDEnergyFormsVideo: Templates.SDEnergyFormsVideo,
  BioStructureLabelingVideo: Templates.BioStructureLabelingVideo,
  BioVirusLifecycleVideo: Templates.BioVirusLifecycleVideo,
  EvolutionSelectionVideo: Templates.EvolutionSelectionVideo,
  ReactionCollisionEnergyVideo: Templates.ReactionCollisionEnergyVideo,
  ElectrochemicalCellVideo: Templates.ElectrochemicalCellVideo,
  OrganicStructureVideo: Templates.OrganicStructureVideo,
  BodySensesHealthVideo: Templates.BodySensesHealthVideo,
  LifeCycleClassificationVideo: Templates.LifeCycleClassificationVideo,
  AcidBaseSafetyVideo: Templates.AcidBaseSafetyVideo,
  LabSafetyVideo: Templates.LabSafetyVideo,
  ParticleMatterStatesVideo: Templates.ParticleMatterStatesVideo,
  InquiryObservationVideo: Templates.InquiryObservationVideo,
  SDMatterStatesVideo: Templates.SDMatterStatesVideo,
  SolarDayNightVideo: Templates.SolarDayNightVideo,
  EarthResourcesEnvironmentVideo: Templates.EarthResourcesEnvironmentVideo,
  SDMixtureSeparationVideo: Templates.SDMixtureSeparationVideo,
  CellStructureVideo: Templates.CellStructureVideo,
  MembraneTransportVideo: Templates.MembraneTransportVideo,
  CellDivisionVideo: Templates.CellDivisionVideo,
  EnzymeMetabolismVideo: Templates.EnzymeMetabolismVideo,
  PhotosynthesisRespirationVideo: Templates.PhotosynthesisRespirationVideo,
  GeneticExpressionVideo: Templates.GeneticExpressionVideo,
  GrowthTimelineVideo: Templates.GrowthTimelineVideo,
  MaterialsEnvironmentVideo: Templates.MaterialsEnvironmentVideo,
  WeatherWaterCycleVideo: Templates.WeatherWaterCycleVideo,
  LabSeparationVideo: Templates.LabSeparationVideo,
  ImmuneResponseVideo: Templates.ImmuneResponseVideo,
  HomeostasisFeedbackVideo: Templates.HomeostasisFeedbackVideo,
  HealthDisorderVideo: Templates.HealthDisorderVideo,
  StructureFunctionVideo: Templates.StructureFunctionVideo,
};

const RenderBySpec: React.FC<{spec: RemotionConceptSpec}> = ({spec}) => {
  const Component = componentMap[spec.component] ?? Templates.EcosystemNetworkVideo;
  return <Component spec={spec} />;
};

export const RemotionRoot: React.FC = () => <>
  {conceptSpecs.map((spec) => (
    <Composition
      key={spec.id}
      id={`${String(spec.row_index).padStart(3,'0')}-${spec.template_id.replace(/[._]/g,'-')}`}
      component={RenderBySpec}
      width={spec.width}
      height={spec.height}
      fps={spec.fps}
      durationInFrames={spec.durationInFrames}
      defaultProps={{spec}}
    />
  ))}
</>;
