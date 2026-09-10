// Generated-runtime shape: [{ id, letter, clue, mechanism }].
// This starter catalog is deliberately small; content/README.md describes the 20/letter release gate.
const entries = {
  A:["Top letter grade","The indefinite article"],
  B:["Honey-maker, in a soundalike","Plan ___"],
  C:["Ocean, in a soundalike","Vitamin found in citrus","A passing grade (barely)","Roman numeral 100"],
  D:["A passing grade","Roman numeral 500","A vitamin nickname","The musical note after C"],
  E:["Online mail, briefly","The base of natural logarithms","Together with C and G, makes the C-Major Chord"],
  F:["A failing grade","A keyboard function key, briefly","Chemical symbol for fluorine"],
  G:["A thousand bucks, informally.","Nothing but a _ thing.",],
  H:["Chemical symbol for hydrogen","A common pencil hardness mark"],
  I: ["What you see with, in a soundalike", "_, Me, My"],
  J:["A bird, in a soundalike","Something you smoke."],
  K:["Metric prefix for thousand","Chemical symbol for potassium","Disinterested affirmation."],
  L:["Something you have to hold.", "The, in Spanish."],
  M:["Roman numeral 1,000","These kind of dashes give away AI writing"],
  N:["Top of a compass"],
  O:["Archaic Interjection."],
  P:["A small green vegetable."],
  Q:["A line of waiting people"],
  R:["A pirate's favorite letter"],
  S:["Makes a plural", "Is, in Spanish."],
  T:["A hot beverage.", "A kind of shirt."],
  U:["Only who can prevent forest fires?", "A kind of turn"],
  V:["The way geese fly", "Roman numeral for 5"],
  W:["Something common for winners","Repeats at the start of an address."],
  X:["Multiplies.","Some signatures.","Former","Women have two."],
  Y:["A question.", "Makes men, men.", "Alternative for Millenials."],
  Z:["Sleeping sound.", "Fire _ missiles!"]
};
export const CLUES = Object.fromEntries(Object.entries(entries).map(([letter, clues]) => [letter, clues.map((clue, index) => ({ id: `${letter}-${index + 1}`, letter, clue, mechanism: 'starter' }))]));

// Each entry is intentionally common, alphabetic, and 6–10 letters long.
export const ANSWERS = [
 ['access','Entry or admission'],['action','Something done'],['almost','Not quite'],['always','At all times'],['amount','A total quantity'],['answer','A response'],['anyone','Any person'],['around','In the vicinity'],['artist','A creative maker'],['attack','A violent assault'],
 ['basket','A woven container'],['beauty','A quality of loveliness'],['become','To grow into'],['before','Earlier than'],['behind','At the back of'],['better','Of higher quality'],['beyond','Farther than'],['bottle','A container for liquid'],['bridge','A span across a gap'],['bright','Giving much light'],
 ['camera','A picture-taking device'],['cannot','Unable to'],['castle','A fortified home'],['center','The middle point'],['chance','A possibility'],['change','To make different'],['cheese','A dairy food'],['circle','A round shape'],['coffee','A caffeinated drink'],['country','A nation'],
 ['create','To make'],['danger','Risk of harm'],['decide','To choose'],['dinner','Evening meal'],['doctor','A medical professional'],['dragon','A mythical reptile'],['drawer','A sliding compartment'],['driver','One who operates a vehicle'],['during','Throughout'],['earthy','Like soil'],
 ['effect','A result'],['effort','Hard work'],['either','One of two'],['energy','Capacity for work'],['enough','As much as needed'],['entire','Whole'],['escape','To get away'],['evening','Later part of the day'],['except','Other than'],['excuse','A reason offered'],
 ['fabric','Cloth'],['family','Related people'],['famous','Well known'],['faster','More quickly'],['father','A male parent'],['fellow','A companion'],['figure','A number or shape'],['finger','A hand digit'],['finish','To complete'],['flower','A blooming plant'],
 ['follow','To come after'],['forest','A large wood'],['friend','A close companion'],['future','Time yet to come'],['garden','A cultivated plot'],['gentle','Mild and kind'],['golden','Made of or like gold'],['ground','Earth beneath us'],['handle','A part for holding'],['happen','To occur'],
 ['health','State of wellness'],['heaven','The sky or paradise'],['hidden','Kept out of sight'],['honest','Truthful'],['honour','High respect'],['horses','Riding animals'],['hostel','A budget lodging place'],['hourly','Every hour'],['humour','Comedy or mood'],['hunter','One who pursues game'],
 ['island','Land surrounded by water'],['itself','The thing in question'],['jacket','An outer garment'],['jungle','Dense tropical forest'],['keeper','One who guards'],['kitchen','Room for cooking'],['ladder','A climbing frame'],['laughing','Making a happy sound'],['leader','One who guides'],['learned','Gained knowledge'],
 ['letter','A written character'],['little','Small'],['living','Alive'],['lonely','Without company'],['lovely','Delightful'],['magical','Having magic'],['market','A place to buy goods'],['master','An expert'],['matter','Physical substance'],['memory','Stored recollection'],
 ['middle','Central part'],['minute','Sixty seconds'],['modern','Of the present time'],['moment','A brief time'],['mother','A female parent'],['mountain','A high natural landform'],['moving','Changing position'],['museum','A collection display'],['mystery','Something unexplained'],['nature','The physical world'],
 ['nearby','Not far away'],['needle','A sewing tool'],['neither','Not one or the other'],['nobody','No person'],['normal','Usual'],['notice','To observe'],['number','A mathematical value'],['object','A thing'],['office','A work room'],['oftener','More frequently'],
 ['orange','A citrus fruit'],['parent','A mother or father'],['people','Human beings'],['period','A span of time'],['person','An individual'],['picture','An image'],['planet','A world orbiting a star'],['player','One taking part in a game'],['please','A polite request word'],['pocket','A small sewn pouch'],
 ['police','Law-enforcement officers'],['potato','A starchy tuber'],['prefer','To like better'],['pretty','Attractive'],['prince','A royal son'],['prison','A place of confinement'],['prizes','Awards'],['proper','Suitable or correct'],['public','Open to all'],['purple','A color mixing red and blue'],
 ['puzzle','A problem to solve'],['rabbit','A long-eared animal'],['really','Truly'],['reason','A cause'],['record','A stored account'],['reduce','To make smaller'],['return','To come back'],['rivers','Natural watercourses'],['rocket','A space vehicle'],['safety','Freedom from danger'],
 ['school','A place for learning'],['season','One division of a year'],['secret','Something kept hidden'],['settle','To resolve'],['shadow','A dark silhouette'],['silver','A gray precious metal'],['simple','Not complicated'],['singer','One who sings'],['single','Only one'],['sister','A female sibling'],
 ['smooth','Even and flat'],['society','An organized community'],['someone','An unspecified person'],['special','Unusual or important'],['spirit','A ghost or inner self'],['spring','A season after winter'],['square','A four-equal-sided shape'],['stable','Firm and steady'],['station','A stopping place'],['street','A public road'],
 ['strong','Powerful'],['summer','The warmest season'],['system','An organized set'],['teacher','One who instructs'],['thankful','Feeling gratitude'],['theory','An explanatory idea'],['thirty','Three tens'],['though','Despite the fact that'],['through','From one side to another'],['ticket','An admission pass'],
 ['together','In company'],['travel','To make a journey'],['trying','Making an effort'],['twelve','One dozen'],['twenty','Two tens'],['unable','Not able'],['uncles','Parent’s brothers'],['undergo','To experience'],['useful','Helpful'],['valley','Low land between hills'],
 ['victory','Success in a contest'],['village','A small settlement'],['violet','A purple-blue flower'],['window','An opening in a wall'],['winter','The coldest season'],['within','Inside'],['wonder','A feeling of amazement'],['wooden','Made of wood'],['worker','One who works'],['worldly','Experienced in life'],
 ['writer','One who writes'],['yellow','A color of sunshine'],['yesterday','The day before today'],['zebras','Striped African animals']
].map(([word, hint]) => ({ word, hint }));
