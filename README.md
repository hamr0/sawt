arabic-tts/
├── data/                   # All data resources
│   ├── dictionaries/       # Phonetic dictionaries
│   │   ├── masterTTS.json  # Main dialect dictionary
│   │   └── syllable_patterns.json
│   ├── rules/              # Phonological rule sets
│   │   ├── gemination_rules.json
│   │   ├── coarticulation_rules.json
│   │   └── dialect_variations/
│   ├── test_cases/         # Sample texts for testing
│   │   ├── msa_samples.txt
│   │   └── dialect_samples/
│   └── resources/          # Additional resources
│       ├── arabic_chars.txt
│       └── special_symbols.txt
│
├── src/                    # Source code
│   ├── core/               # Main processing modules
│   │   ├── preprocessing.py
│   │   ├── syllabifier.py
│   │   ├── ipa_mapper.py
│   │   ├── dialect_processor.py
│   │   └── output_generator.py
│   │
│   ├── dialects/           # Dialect-specific implementations
│   │   ├── msa.py
│   │   ├── egyptian.py
│   │   ├── gulf.py
│   │   ├── levantine.py
│   │   └── maghreb.py
│   │
│   ├── utils/              # Helper functions
│   │   ├── file_io.py
│   │   ├── text_tools.py
│   │   └── validation.py
│   │
│   ├── api/                # Integration points
│   │   ├── web_api.py
│   │   └── cli_interface.py
│   │
│   └── main.py             # Entry point
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   │   ├── test_syllabifier.py
│   │   └── test_dialects.py
│   │
│   ├── integration/        # Integration tests
│   │   ├── test_full_pipeline.py
│   │   └── test_performance.py
│   │
│   └── test_data/          # Test data samples
│       ├── short_phrases/
│       └── long_texts/
│
├── config/                 # Configuration files
│   ├── app_config.yaml
│   └── logging_config.yaml
│
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md
│   ├── DATA_STRUCTURE.md
│   ├── API_REFERENCE.md
│   └── dialect_specs/      # Dialect-specific docs
│
├── scripts/                # Utility scripts
│   ├── data_import.py
│   ├── batch_processor.py
│   └── stats_generator.py
│
├── requirements.txt        # Python dependencies
├── .gitignore
├── LICENSE
├── pyproject.toml          # Build configuration
└── README.md               # Project overview

Arabic Text to IPA Flow
graph TD
A[Input Text] --> B(Tokenize)
B --> C[Analyze Characters]
C --> D[Group Arabic Words]
D --> E[Syllabify Words]
E --> F[Map to IPA]
F --> G[Apply Dialect Rules]
G --> H[Output JSON]