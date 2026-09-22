"""File to generate text for progressive trials"""

import csv


def sanitize_quotes(text: str) -> str:
    """
    Replace left/right quote characters (curly or straight) with
    {LQ} / {RQ} tokens.

    Handles:
      - Curly double quotes: left-double-quote and right-double-quote
    """
    text = text.replace("\u201c", "{LQ}").replace("\u201d", "{RQ}")
    return text

def get_next(pieces: dict, cutoff: int, para_starts: set) -> str:
    """
    Get the next piece of text after a given cutoff.
    """
    next = pieces.get(cutoff + 1, "")
    next = sanitize_quotes(next)
    if cutoff + 1 in para_starts:
        next = "{s}" + next

    return next

def build_trials(pieces: dict, cutoffs: list, para_starts: set, sep_within_group: str = " ") -> list:
    """
    Build the 3 progressive text-box trials for a research participant.

    Parameters
    ----------
    pieces : dict
        Maps piece number (int, 1-indexed) -> text for that piece
        (usually 1-2 sentences).
    cutoffs : list of 3 ints
        [c1, c2, c3] in increasing order. c1 = end of trial 1,
        c2 = end of trial 2, c3 = end of trial 3.
    para_starts : set of int
        Set of cutoff indices that start a new paragraph.
    sep_within_group : str
        Separator to join pieces within the same group (default: single space).

    Returns
    -------
    list of 6 strings: [trial1_text, trial1_next, trial2_text,
                        trial2_next, trial3_text, trial3_next]

    Rules
    -----
    For trial t (t = 1, 2, 3), the text shown is pieces 1..cutoffs[t-1],
    but the paragraph breaks are shifted by one piece to reflect that
    each trial is a two-step reveal: the single newly-revealed piece
    right after a previous cutoff gets grouped with the "old" text,
    since that's the piece the participant sees appear first before
    the rest of the new content follows.

    Concretely, for cutoffs [c1, c2, c3]:
      - Trial 1: pieces 1..c1                          (no break)
      - Trial 2: pieces 1..(c1+1)  \\n\\n  (c1+2)..c2
      - Trial 3: pieces 1..(c1+1)  \\n\\n  (c1+2)..(c2+1)  \\n\\n  (c2+2)..c3

    In general, for trial t, the break points occur right after
    (prior_cutoff + 1) for every prior cutoff, and the final segment
    always ends at that trial's own cutoff.
    """
    if len(cutoffs) != 3:
        raise ValueError("cutoffs must have exactly 3 values: [c1, c2, c3]")

    c1, c2, c3 = cutoffs
    if not (c1 < c2 < c3):
        raise ValueError("cutoffs must be strictly increasing: c1 < c2 < c3")

    max_piece = max(pieces.keys())
    if c3 > max_piece:
        raise ValueError(f"c3 ({c3}) > the number of pieces ({max_piece})")

    def join_range(start: int, end: int) -> str:
        """Join pieces[start..end] inclusive in order,
        with quotes sanitized to {LQ}/{RQ} tokens."""
        return sep_within_group.join(
            sanitize_quotes(pieces[i]) for i in range(start, end + 1) if i in pieces
        )

    def build_trial_text(current_cutoff: int, prior_cutoffs: list) -> str:
        # Every prior cutoff creates a segment boundary at (prior_cutoff + 1);
        # the final segment always ends at current_cutoff.
        ends = [c + 1 for c in prior_cutoffs] + [current_cutoff]
        #2, 6, 11
        starts = [1]
        for e in ends[:-1]:
            # 1, 3, 7
            starts.append(e + 1)
        segments = [join_range(s, e) for s, e in zip(starts, ends)]
        return r"\n\n".join(segments)

    trial1 = build_trial_text(c1, [])
    trial2 = build_trial_text(c2, [c1])
    trial3 = build_trial_text(c3, [c1, c2])

    next1 = get_next(pieces, c1, para_starts)
    next2 = get_next(pieces, c2, para_starts)
    next3 = get_next(pieces, c3, para_starts)

    return [trial1, next1, trial2, next2, trial3, next3]

def art2():
    art2 = {1: "Labubu toys, the grinning fuzzy trinkets that became a global sensation last year, are going to be the stars of a Hollywood movie, joining a growing list of beloved characters to jump from store shelves to the big screen. (Hi, Barbie!)",
                2: "Sony and the Chinese retailer Pop Mart, which exclusively sells the dolls, announced on Thursday that they were developing a Labubu feature film.",
                3: "Paul King, the British screenwriter and director behind “Paddington” and “Wonka,” will produce and direct the film, according to a statement from the companies.",
                4: "King will collaborate with Steven Levenson, who wrote the book for the musical “Dear Evan Hansen,” on the screenplay.",
                5: "The announcement offered few details and did not give a release date.",
                6: "But the film will become the latest to turn beloved toys into the stars of a major movie, along with Barbie, Lego, the Transformers and others.",
                7: "The close link between movies and merchandising is often traced back to the immense success of the original “Star Wars” trilogy in the late 1970s and early ’80s, intellectual property experts said.",
                8: "“It took seriously the idea of your intellectual property being commercialized on quite a few different channels,” Emily Hudson, a professor of law at the University of Oxford, said of “Star Wars.”",
                9: "But whereas “Star Wars” started as a movie and became a major merchandising success, that model has been inverted lately.",
                10: "“Now you come up first with the merchandise and then you retrofit some sort of cinematic universe or some television show around the toys,” said Luke McDonagh, a professor at the London School of Economics who researches intellectual property law.",
                11: "That strategy has paid huge dividends.",
                12: "“The Lego Movie,” made by Warner Bros. and the Lego Group, took in nearly $500 million at the global box office in 2014, and was followed by a sequel and two spinoffs.",
                13: "Paramount Pictures and Hasbro have turned the Transformers action-figure line into a $5 billion big-screen franchise.",
                14: "The toy company Mattel has moved to turn its brands into full-fledged entertainment brands, including “Barbie,” the live-action adventure starring Margot Robbie that earned nearly $1.5 billion.",
                15: "A “Polly Pocket” movie, co-produced by Reese Witherspoon’s production company, is in the works.",
                16: "“Characters are now the most valuable kind of intellectual property,” said Dev Gangjee, a professor of intellectual property law at the University of Oxford. “They straddle all these formats.”",
                17: "The commercial successes and the critical acclaim of many of these movies have changed the dynamics of how these kinds of projects are perceived."
                }
    cut2_a = [9, 13, 16]
    para_starts = {2, 5, 7, 8, 9, 10, 11, 14, 16, 17}

    art2_trials = build_trials(art2, cut2_a, para_starts)
    for text in art2_trials:
        print(text)
        print("\n---\n")

    with open('IEsetup.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Text'])
        for item in art2_trials:
            writer.writerow([item])

def art3():
    art3 = {1: "When it opened in 1984, the Costco on West Dimond Boulevard in Anchorage did not seem like the future of food.",
            2: "A glorified shed the color of stale coffee, the warehouse offered the sort of products and deals Alaskans go crazy for: mammoth quantities of staples like peanut butter and tomato sauce, along with local favorites such as caribou sausage.",
            3: "The state's extreme environment and the need to travel hours or even days for groceries made it a hit right off the bat.",
            4: "Today the parking lot, full of jacked-up, Thuled-out 4x4s on studded tires and mobile homes that look more like mobile fortresses, has a bit of an edge for a grocery store.",
            5: "There's something edgy about the inventory, too: neoprene survival suits, meat grinders, gun safes.",
            6: "Inside the vast store, overloaded shopping carts seemingly pilot themselves down the aisles.",
            7: "One was pushed by Gabriella Pelesasa, a teenager who was buying, among other things, a pair of whole pigs, at 45 pounds each.",
            8: "As her sister sat on the cart eating a Costco hot dog, Ms. Pelesasa reported simply, “They have bigger versions of what we want.”",
            9: "Though the Anchorage location, one of the retailer's first, once seemed like a survivalist outlier, today it shows how visionary Costco was.",
            10: "“In 2020, about one-quarter of the population stockpiled nonperishable foods,” said Jennifer Mapes-Christ of the market research firm Packaged Facts.",
            11: "Today, more than half do. Ms. Mapes-Christ said that while the pandemic was an accelerant, the trend began before that, driven by anxieties about climate change and economic instability.",
            12: "In 2019, one quarter of U.S. consumers shopped at Costco. Today it is nearly one-third.",
            13: "Costco is the third-largest retailer in the world, behind only Amazon and Walmart.",
            14: "But the success of Costco goes far beyond hoarding.",
            15: "The company has hacked the psyche of the American consumer, appealing to both the responsible-shopping superego (“Twelve cans of tuna for $18!”) and the buy-it-now id (“I deserve that 98-inch flat screen”).",
            16: "Ostensibly, Costco is a discount store, a place to save money and stretch your grocery dollar, but it is also an aspirational shopping experience, feeding that most American of appetites: conspicuous consumption."
            }

    cut3 = [[1,4, 7], [1, 6, 11], [1, 5, 10], [2, 5, 10],
            [2, 7, 12], [2, 6, 11], [3, 8, 13], [3, 8, 14],
            [3, 9, 13], [5, 9, 14], [4, 8, 13], [4, 10, 15],
            [7, 12, 15], [6, 11, 14], [9, 12, 15]]

    para_starts3 = {4, 6, 8, 9, 10, 12, 14, 16}

    with open("IEsetup3.csv", "w") as f:
        pass
    for cut in cut3:
        trial = build_trials(art3, cut, para_starts3)
        with open('IEsetup3.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(trial)

def art4():
    art4 = {
        1: "If you think your daily doses of espresso or Earl Grey sharpen your mind, you just might be right, new science suggests.",
        2: "A large new study provides evidence of cognitive benefits from coffee and tea — if it's caffeinated and consumed in moderation: two to three cups of coffee or one to two cups of tea daily.",
        3: "People who drank that amount for decades had lower chances of developing dementia than people who drank little or no caffeine, the researchers reported.",
        4: "They followed 131,821 participants for up to 43 years.",
        5: "“This is a very large, rigorous study conducted long term among men and women that shows that drinking two or three cups of coffee per day is associated with reduced risk of dementia,” said Aladdin Shadyab, an associate professor of public health and medicine at the University of California, San Diego, who wasn't involved in the study.",
        6: "The findings, published Monday in JAMA, don't prove caffeine causes these beneficial effects, and it's possible other attributes protected caffeine drinkers' brain health.",
        7: "But independent experts said the study adjusted for many other factors, including health conditions, medication, diet, education, socioeconomic status, family history of dementia, body mass index, smoking and mental illness.",
        8: "The caffeine correlation held regardless of whether people had genetic risk factors for Alzheimer's or other dementias.",
        9: "The study, funded by the National Institutes of Health, didn't distinguish between dementia types.",
        10: "Some previous studies haven't found cognitive benefits from caffeine, but those studies often had limitations like shorter time periods or one-time assessments of diet, experts said.",
        11: "The new study aligns with a growing body of research “that's suggested caffeinated coffee may reduce risk of age-related chronic diseases,” Dr. Shadyab said.",
        12: "Researchers followed participants in two long-running studies of medical practitioners: women in the Nurses' Health Study and men in the Health Professionals Follow-up Study.",
        13: "Typically in their mid-40s or early 50s at the start, participants received repeated surveys about diet, health and lifestyle factors.",
        14: "During that time, 11,033 participants developed dementia, documented with death certificates or physician diagnoses.",
        15: "Compared with people who consumed virtually no caffeine, people who drank between one and five eight-ounce cups of caffeinated coffee had about 20 percent less dementia risk.",
        16: "Those who drank at least one cup of caffeinated tea daily had about 15 percent less risk.",
        17: "But beyond two and a half cups of coffee daily, the advantage plateaued, possibly because humans cannot metabolize any more of the bioactive compounds in coffee and tea, said the study's senior author, Dr. Daniel Wang, an epidemiologist specializing in neurodegenerative diseases at Mass General Brigham health system.",
        18: "Dr. Wang, who drinks about three cups each of coffee and green tea daily, said the study didn't find anything negative about larger caffeine quantities.",
        19: "But some studies suggest exceeding moderate amounts can harm health by disrupting sleep or exacerbating anxiety, said Dr. Fang Fang Zhang, an epidemiologist at Tufts University's Friedman School of Nutrition Science and Policy, who wasn't involved in the new research."
    }

    cut4 = [[1,4, 8], [1, 5, 9], [2, 5, 10], [2, 6, 11],
            [3, 7, 12], [3, 7, 13], [4, 8, 14], [6, 12, 15],
            [9, 14, 17], [10, 15, 17], [11, 16, 18], [13, 16, 18]]

    para_starts3 = {2, 3, 5, 6, 8, 10, 12, 15, 17, 18}

    with open("IEsetup4.csv", "w") as f:
        pass
    for cut in cut4:
        trial = build_trials(art4, cut, para_starts3)
        with open('IEsetup4.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(trial)

def art5():

    art5 = {
    1: "So you think your only choice during a long layover or a flight delay is to suffer in the airport terminal? Think again.",
    2: "But be prepared to pay handsomely one way or another for the alternative.",
    3: "The airline lounge competition is heating up around the globe, and two new entrants, American and United, have, somewhat belatedly, become serious contenders.",
    4: "Like the difference between first-class and economy seats, the luxury lounges offered by many major airlines are yet another way in which air travel is separating the haves from the have-nots.",
    5: "Entry usually requires the purchase of a business- or first-class ticket, and some VIP lounges charge thousands of dollars per visit by individuals or small groups of travelers.",
    6: "There are some exceptions for holders of certain credit cards, and occasionally a traveler can make a one-time visit for a relatively low fee.",
    7: "But regardless of the cost, lounge access has become paramount for business travelers, especially those on overnight flights from the Northeastern United States to Europe, experts say.",
    8: "They want to shower and eat fresh food in the lounge, and then sleep on their flight, so when they arrive in Europe they can head directly to their meeting.",
    9: "For other travelers, lounges can provide “a reprieve from the chaos of the airport, an oasis from the storm,” said Jack Ezon, president of New York-based Ovation Vacations, an upscale leisure travel agency.",
    10: "To Michael Holtz, owner of SmartFlyer, another upscale travel agency, a lounge can extend a luxury hotel experience.",
    11: "Guests staying in certain high-end suites at the Rosewood London, for example, qualify for free access to the VIP private terminal at London's Heathrow Airport.",
    12: "Qatar Airways' Al Safwa first-class lounge at Hamad International Airport in Doha, Qatar, offers 12 private bedrooms.",
    13: "American Airlines offers Flagship Lounge access to first- and business-class passengers on transcontinental and international flights and has opened new ones at John F. Kennedy International Airport in New York, Miami International Airport, Los Angeles International Airport and O'Hare International Airport outside of Chicago since last year.",
    14: "The lounges have hot and cold buffets, wine, Champagne and create-your-own cocktails, showers and quiet rooms. All lounges except O'Hare's also have restaurant-style dining for first-class passengers.",
    15: "United opened its first Polaris Lounge — available only to passengers flying in its Polaris, or business class, and to first-class passengers on Star Alliance airlines' flights — at O'Hare in December 2016.",
    16: "Since spring, it has opened other lounges at San Francisco International Airport, Newark Liberty International Airport in New Jersey and George Bush Intercontinental Airport in Houston.",
    17: "Other Polaris lounges are also planned in Los Angeles and at Washington Dulles International Airport.",
    18: "These will feature a restaurant offering local cuisine; relaxation areas, including daybeds with Saks Fifth Avenue bedding; and shower suites with valet service.",
    19: "But American's and United's lounges are in many ways overshadowed by older and newer top-tier airport lounges operated by carriers based outside the United States."
    }

    cut5 = [[4, 8, 14], [11, 16, 18],[1, 5, 9], [2, 5, 10],
            [3, 7, 13], [1, 4, 8], [6, 12, 15], [10, 15, 17],
            [13, 16, 18], [3, 7, 12], [9, 14, 17],[2, 6, 11]]

    para_starts5 = {2, 3, 4, 5, 7, 9, 10, 13, 15, 17, 19}

    with open("IEsetup5.csv", "w") as f:
        pass
    for cut in cut5:
        trial = build_trials(art5, cut, para_starts5)
        with open('IEsetup5.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(trial)

def main():
    """Main function for testing"""

    art6 = {
        1: "Alex Honnold, a rock climber who was the subject of the Oscar-winning documentary “Free Solo,” successfully climbed the 1,667-foot-tall skyscraper Taipei 101 in Taiwan on Sunday, without a rope.",
        2: "Scaling a building that tall is not like climbing a mountain.",
        3: "Those in the club of just a dozen or so known skyscraper climbers worldwide say the activity comes with unique physical and mental demands.",
        4: "It is also a largely underground sport because it is usually illegal.",
        5: "Alain Robert, a Frenchman who has scaled some 200 buildings since the 1990s, mostly with his bare hands, said that he has been arrested more than 170 times.",
        6: "“You feel like you're literally in a movie,” Mr. Robert said, with “cops that are trying to catch the bad guy climbing the building.”",
        7: "The obvious risks make it rare for someone to obtain permission to climb a tall building, as Mr. Honnold did.",
        8: "His climb on Sunday was broadcast live on Netflix.",
        9: "“I've never been willing to get arrested,” the 40-year-old said in a podcast recorded before the climb.",
        10: "Unlike the serene natural landscape surrounding climbers on routes like El Capitan in Yosemite National Park, which Mr. Honnold scaled in 2017, skyscraper climbers must overcome urban noise, crowds and, occasionally, police officers determined to arrest them.",
        11: "“You feel like King Kong in the city,” said Titouan Leduc, 24, a French climber who scaled Warsaw's Varso Tower, the tallest skyscraper in the European Union, last year.",
        12: "He was briefly arrested after that.",
        13: "Those who have climbed skyscrapers say their bodies face different demands compared with rock climbing.",
        14: "According to Dan Goodwin, who in 1986 climbed the CN Tower in Toronto — then the tallest structure in the world — skyscraper climbing mainly comes down to repetitiveness versus variety.",
        15: "On a rock face, each move presents a new puzzle: climbers' hands search for different holds — crimps, jugs, slopers — and they constantly adapt their bodies.",
        16: "But along the side of a building, climbers repeat the same few movements hundreds of times to pass over dozens of stories of windows, steel bars and concrete gaps."
    }

    cut6 = [[1, 4, 9], [1, 5, 10], [2, 5, 10], [2, 6, 11],
            [3, 7, 12], [3, 8, 13], [4, 9, 14], [6, 11, 14],
            [7, 12, 15], [8, 13, 15]]


    para_starts6 = {2, 4, 6, 7, 9, 10, 11, 13, 14, 15}

    with open("IEsetup6.csv", "w") as f:
        pass
    for cut in cut6:
        trial = build_trials(art6, cut, para_starts6)
        with open('IEsetup6.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(trial)


if __name__ == "__main__":
    # --- Example usage ---
    main()


    """example_pieces = {
        1: "Sentence one of the article.",
        2: "Sentence two follows here.",
        3: "Sentence three adds more detail.",
        4: "Sentence four continues the thought.",
        5: "Sentence five wraps up the first section.",
        6: "Sentence six starts a new idea.",
        7: "Sentence seven expands on it.",
        8: "Sentence eight gives an example.",
        9: "Sentence nine offers a counterpoint.",
        10: "Sentence ten summarizes the section.",
        11: "Sentence eleven is the final piece.",
    }

    cutoffs = [1, 5, 11]
    trials = build_trials(example_pieces, cutoffs)

    for i, t in enumerate(trials, start=1):
        print(f"--- Trial {i} ---")
        print(t)
        print()"""