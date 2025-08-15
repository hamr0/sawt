def print_syllabification(result):
    for word in result["words"]:
        if word["type"] != "arabic_word":
            continue

        print(f"\nWord: {word['original']}")
        print("Syllables:")
        for syl in word["syllables"]:
            print(f"  {syl['syllable']:5} {syl['pattern']:4} → {syl['ipa']}")