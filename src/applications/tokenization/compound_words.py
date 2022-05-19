# source: https://da.wiktionary.org/wiki/Kategori:Sammensatte_ord_på_dansk
# tagger: Kenneth C. Enevoldsen
# Words which the tagger did not understand (e.g. some icelandic words) were removed
#
# "|" indicates primary split (into compound words)
# "&" indicates secondary split (used in case of compound word existing of a multiple
# compounds) e.g. blindtarmsbetændelse consist of two compounds "blindtarm" "betændelse"
# with a 'lim-s' ("s"), but blindtarm is itself a compound, namely "blind", "tarm".
ordliste = """A|-|aktie
A3|-|format
A4|-|format
A5|-|format
abe|bur
abe|fest
abe|kat
abe|katte&streg
abe|menneske
abe|træ
abort|klinik
abort|lovgivning
abort|modstander
abort|tilhænger
absorptions|lyd&dæmper
absorptions|varme&pumpe
aconto|betaling
adresse|ændring
advent|s|krans
affald|s|sæk
afløvning|s|middel
afsked|s|brev
afsked|s|gave
aften|falk
aften|s|mad
ager|høne
ager|ugle
akvarie|fisk
alder|s|bestemmelse
alder|s|forskel
almen|nyttig
altan|dør
andet|sprog
ansættelses|kontrakt
ansøgnings|frist
anæstesi|læge
appelsin|juice
appelsin|saft
april|s|nar
arbejd|s|handske
arm|bånd
arm|bånd&s&ur
arm|hule
arm|sved
asyl|ret
atom|affald
atom|bombe
atom|fysik
atom|kraft
atom|kraft&værk
avis|and
avis|kiosk
bade|bukser
bade|ferie
bade|for&hæng
bade|kar
bade|værelse
bade&værelse|s|dør
badminton|bane
badminton|ketsjer
badminton|net
badminton|spiller
bag|ben
bag|dør
baggrund|s|musik
bag|hus
bag|lomme
bag|lår
bakke|top
bakterie|infektion
banan|blad
banan|flue
banan|palme
banan|plantage
banan|skræl
bank|direktør
bank|konto
barber|kniv
barber|skum
barne|barn
barne|dåb
barne|vogn
barsel|s|orlov
basketball|kamp
basketball|klub
basketball|spiller
bedste|mor
begyndelse|s|bogstav
beklædning|s|genstand
ben|væv
benzin|afgift
benzin|bil
benzin|dunk
benzin|motor
benzin|selskab
beskyttelse|s|briller
betaling|s|middel
bi|avler
bibel|figur
bidrag|s|yder
bil|batteri
bil|dæk
bil|dør
bil|ferie
bil|færge
bil|hjul
billed|bog
billet|automat
billet|kontor
billet|kontrollør
bil|radio
bil|rude
bil|trafik
bil|tyv
bil|tyveri
bil|vask
binde|bogstav
binde|hinde
binde|væv
biograf|besøg
biograf|billet
biograf|direktør
biograf|ejer
biograf|film
biograf|forestilling
biograf|gænger
biograf|lærred
biograf|publikum
biograf|reklame
biograf|sal
biograf|stol
biograf|tur
birke|pollen
birke|skov
bistand|s|hjælp
bi|stik
bi|virkning
bjerg|and
bjerg|art
bjerg|kæde
bjerg|lærke
bjerg|salamander
bjerg|tinde
bjerg|top
bjerg|vipstjert
bjælde|klang
bjørne|unge
blad|mave
blanding|s|skov
blind|gyde
blind&tarm|s|betændelse
blind&tarm|s|operation
blis|gås
blis|høne
blod|bank
blod|bus
blod|celle
blod|donor
blod|dråbe
blod|legeme
blod|mangel
blod|plade
blod|prøve
blod|pølse
blod|s|dråbe
blod|suger
blod|sukker
blod|transfusion
blod|tryk
blod|type
blod|åre
blomme|træ
blomster|bed
blomster|flue
blyant|s|pidser
blå|bær
blå|hals
blå|hval
blå|musling
blå|skimmel&ost
blære|betændelse
blæse|bælg
blæse|instrument
blæse|vejr
blød|dyr
boarding|kort
body|shampoo
bog|anmeldelse"""


# split words into compounds and subcomponds
orddele = [
    [compound.split("&") for compound in word.split("|")]
    for word in ordliste.split("\n")
]


sammensatte_ord = {
    "".join([subc for compound in ord for subc in compound]): ord for ord in orddele
}

# source: https://sproget.dk/raad-og-regler/ordlister/sproglige-ordlister/ordforbindelser-i-et-eller-flere-ord

text = """aber dabei	altid sådan	
a c./ac. (fork. for a conto/aconto)	altid valgfrit	
a cappella	altid sådan	
a cappella-kor	altid sådan	
accent aigu	altid sådan	Brugen af accent aigu i ord som idé og kupé gøres frivillig.
accent grave	altid sådan	
a conto/aconto	altid valgfrit	
acontobeløb/a conto-beløb	altid valgfrit	
actionfilm	altid sådan	
ad acta	altid sådan	
a dato-veksel	altid sådan	
ad gangen	altid sådan	
ad hoc	altid sådan	
ad hoc-udvalg	altid sådan	
ad libitum	altid sådan	
af hænde	altid sådan	
af sted/afsted	altid valgfrit	
afstedkomme	altid sådan	
ahaoplevelse	altid sådan	
aids-patient/aidspatient	altid valgfrit	
ajour	altid sådan	
a la	altid sådan	
a la carte	altid sådan	
a la carte-ret	altid sådan	
a la grecque-bort	altid sådan	
al den stund	altid sådan	
al dente	altid sådan	
al fresco	altid sådan	
allerbedst	altid sådan	
alle sammen/allesammen	altid valgfrit	
alle tiders/alletiders	altid valgfrit	
alle vegne/allevegne	altid valgfrit	
all right	altid sådan	
allround	altid sådan	
alter ego	altid sådan	
alt for	altid sådan	
alt i alt	altid sådan	
alt imens	altid sådan	
alting	altid sådan	
alt sammen	altid sådan	
angina pectoris	altid sådan	
a posteriori	altid sådan	
a priori	altid sådan	
a priori-antagelse	altid sådan	
apropos	altid sådan	
art deco	altid sådan	
art deco-stil	altid sådan	
au pair	altid sådan	
au pair-pige	altid sådan	
a vista	altid sådan	
a vista-veksel	altid sådan	
backup	altid sådan	
bagefter	uden styrelse: skrives i et ord	Bagefter gik de ud og tømte Berlins butikker.
bag efter/bagefter	med styrelse: skrives valgfrit i et eller to ord	Han har løbet bag efter/bagefter mig nogen tid mens jeg har lært at cykle.
bagi	uden styrelse: skrives i et ord	Det gav et enormt puf bagi.
bag i/bagi	med styrelse: skrives valgfrit i et eller to ord	De tænker sig skam om, selv om/selvom samfundet puffer dem bag i/bagi køen.
bagom	uden styrelse: skrives i et ord	Fischer vender sig halvt bagom, desperat og hjælpeløs.
bag om/bagom	med styrelse: skrives valgfrit i et eller to ord	Jeg gik bag om/bagom huset og hen til køkkenindgangen.
bagover	altid sådan	
bagpå	uden styrelse: skrives i et ord	Jeg er ved at skubbe en løve ind i klædeskabet, tænkte Max og puffede løven bagpå.
bag på/bagpå	med styrelse: skrives valgfrit i et eller to ord	Nederlaget 9. april kom ikke bag på/bagpå ham.
bagud	altid sådan	
bagude	altid sådan	
bagved	uden styrelse: skrives i et ord	Tyskerne bagved og svenskerne til venstre var en generation ældre.
bag ved/bagved	med styrelse: skrives valgfrit i et eller to ord	Jeg ved at bestyrelsen står ikke bag ved/bagved den slags.
bel canto	altid sådan	
bel canto-kor	altid sådan	
belle de boskoop	altid sådan	
billig bog	altid sådan	Det var en meget billig bog
billigbog 'bog i mindre format og i mere beskedent udstyr end en almindelig bog'	altid sådan	Forlaget genudsender tre billigbøger i en meget gaveegnet hardbackudgave.
bittelille	altid sådan	
bittesmå	altid sådan	
blackout	altid sådan	
boksershorts	altid sådan	
broderie anglaise	altid sådan	
broderie anglaise-kjole	altid sådan	
bungeejumping	altid sådan	
bøf stroganoff	altid sådan	
børn og unge-udvalg (jf. børne- og ungeudvalg)	altid sådan	
cafe au lait/café au lait	altid valgfrit	
carte blanche	altid sådan	
castrum doloris	altid sådan	
centerforward	altid sådan	
charge d'affaires/chargé d'affaires	altid valgfrit	
check-in/checkin	altid valgfrit	
cherry brandy	altid sådan	
cire perdue	altid sådan	
comeback	altid sådan	
commedia dell'arte	altid sådan	
comme il faut	altid sådan	
con amore	altid sådan	
concerto grosso	altid sådan	
cordon bleu	altid sådan	
country og western	altid sådan	
country og western-musik	altid sådan	
coverup	altid sådan	
crepe de chine	altid sådan	
crepe georgette	altid sådan	
crepes suzette	altid sådan	
curriculum vitæ/curriculum vitae	altid valgfrit	
da capo (adv.)	altid sådan	
dacapo (sb.)	altid sådan	
dags dato-kvittering	altid sådan	
dags tid	altid sådan	
dag til dag-rente	altid sådan	
danskamerikaner	altid sådan	
dark horse	altid sådan	
de facto	altid sådan	
de facto-anerkendelse	altid sådan	
de facto-flygtning	altid sådan	
de jure	altid sådan	
de jure-anerkendelse	altid sådan	
delirium tremens	altid sådan	
den gang	med styrelse: skrives i to ord	Det var også den gang, hvor far og jeg gik i kælderens værksteds- og hobbyrum.
dengang	uden styrelse: skrives i et ord	I begyndelsen af 1900-tallet fik man præmie for at skyde en ugle, helt op til 50 øre, og det var mange penge dengang.
der efter	med styrelse: skrives i to ord	De to kadetter der efter traditionen spilles af piger.
derefter	uden styrelse: skrives i et ord	Straks derefter skød tiltalte et skud ind i væggen.
der fra	med styrelse: skrives i to ord	Alt i alt satses der fra mange sider.
derfra	uden styrelse: skrives i et ord	Hun kan ikke slippe derfra.
der hen	med styrelse: skrives i to ord	Også i denne lignelse vises der hen til et nyt liv.
derhen	uden styrelse: skrives i et ord	For at komme derhen måtte han over grøften i vejkanten og gennem sommerhusområdet.
derhenad	altid sådan	
derhenhørende	altid sådan	
derhenimod	altid sådan	
derhenne	altid sådan	
derhennefra	altid sådan	
derhjem	altid sådan	
derhjemad	altid sådan	
derhjemme	altid sådan	
derhjemmefra	altid sådan	
derhos	altid sådan	
der i	med styrelse: skrives i to ord	Stenen har naturligvis ligget der i tusinder af år.
deri	uden styrelse: skrives i et ord	Deri har de fuldstændig ret.
der iblandt	med styrelse: skrives i to ord	Han står der iblandt de andre.
deriblandt	uden styrelse: skrives i et ord	Fem hollændere, deriblandt direktøren for et tømmerfirma, blev anholdt i byen Breda.
derigennem	altid sådan	
derimellem	altid sådan	
der imod	med styrelse: skrives i to ord	En byggesagkyndig ingeniør der imod betaling vil følge og inspicere byggeriet.
derimod	uden styrelse: skrives i et ord	Vælger man derimod den 2650 meter høje tinde Paranal, som ligger langt mod nord, må der foretages kostbare nyinvesteringer.
derind	altid sådan	
derindad	altid sådan	
derinde	altid sådan	
derindefra	altid sådan	
derindimellem	altid sådan	
derindomkring	altid sådan	
derindunder	altid sådan	
der med	med styrelse: skrives i to ord	Og så står Harald der med knyttede næver.
dermed	uden styrelse: skrives i et ord	I tredje sejlads vandt Susanne Ward, og dermed kom der for tredje gang i træk en pige først over stregen.
derned	altid sådan	
dernedad	altid sådan	
dernede	altid sådan	
dernedefra	altid sådan	
dernedenfor	altid sådan	
dernedeomkring	altid sådan	
dernedomkring	altid sådan	
dernedtil	altid sådan	
dernæst	altid sådan	
derom	altid sådan	
der omkring	med styrelse: skrives i to ord	I højsæsonen er der omkring 600 mennesker til de daglige forevisninger.
deromkring	uden styrelse: skrives i et ord	Mon ikke det har været i 1910 eller deromkring?
deromme	altid sådan	
derommefra	altid sådan	
derop	altid sådan	
deropad	altid sådan	
deropomkring	altid sådan	
deroppe	altid sådan	
deroppefra	altid sådan	
deroveni	altid sådan	
derovenover	altid sådan	
der over	med styrelse: skrives i to ord	Så er der over en halv million tilbage.
derover	uden styrelse: skrives i et ord	Persillegartneren var taget derover for at se på sjældne blomster.
deroverfor	altid sådan	
derovre	altid sådan	
derovrefra	altid sådan	
der på	med styrelse: skrives i to ord	Foreløbig ligger der på ministerens bord kun papirer om tre regioner.
derpå	uden styrelse: skrives i et ord	Charter-cyklerne efterlod vi ved slusen i Carcassonne til afhentning dagen derpå.
dersom	altid sådan	
dersteds	altid sådan	
der til	med styrelse: skrives i to ord	I den australske vinter er der til gengæld tid til ferie.
dertil	uden styrelse: skrives i et ord	Men at nå dertil har kostet meget arbejde.
dertilhørende	altid sådan	
derud	altid sådan	
derudad	altid sådan	
derudaf	altid sådan	
derude	altid sådan	
derudefra	altid sådan	
derudenfor	altid sådan	
derudeomkring	altid sådan	
derudfor	altid sådan	
derudfra	altid sådan	
derudover	altid sådan	
der under	med styrelse: skrives i to ord	I nyhedsformidlingen arbejdes der under et stort pres.
derunder	uden styrelse: skrives i et ord	Hvis kroppens kernetemperatur falder til 30 grader eller derunder, er det direkte livsfarligt.
derved	altid sådan	
des værre	altid sådan	Jo længere arbejdsløsheden varer, des værre er det.
desværre	altid sådan	Desværre kunne partiet ikke stemme for finansloven
deus ex machina	altid sådan	
diner transportable	altid sådan	
don juan	altid sådan	
don quijote/don quixote	altid valgfrit	
drive-in/drivein	altid valgfrit	
droit moral	altid sådan	
dropout	altid sådan	
duc d'albe	altid sådan	
dødsensfarlig	altid sådan	
dødtræt	altid sådan	
earl grey-te	altid sådan	
eau de cologne	altid sådan	
eau de toilette	altid sådan	
eftersom	altid sådan	
en bloc	altid sådan	
en detail	altid sådan	
enetages	altid sådan	
en face	altid sådan	
en famille	altid sådan	
enfant terrible	altid sådan	
en gang	altid sådan	En gang om ugen spiller han tennis.
engang	altid sådan	Der var engang en mand, han boede i en spand.
en garde	altid sådan	
en gros/engros	altid valgfrit	
engrosforretning/en gros-forretning	altid valgfrit	
en masse	altid sådan	
en miniature	altid sådan	
en passant	altid sådan	
en suite	altid sådan	
en vogue	altid sådan	
et cetera/etcetera	altid valgfrit	
etværelses	altid sådan	
etårs	altid sådan	
ex auditorio	altid sådan	
ex cathedra	altid sådan	
executor testamenti	altid sådan	
ex officio	altid sådan	
ex tempore	altid sådan	
fait accompli	altid sådan	
fakturadato	altid sådan	
falde på halen-komedie	altid sådan	
faux pas	altid sådan	
feedback	altid sådan	
femme fatale	altid sådan	
fifty-fifty	altid sådan	
fire hundrede og enoghalvtreds	altid sådan	
flydende krystal-skærm	altid sådan	
followup	altid sådan	
force majeure	altid sådan	
for længst	altid sådan	
forneden	altid sådan	
for nylig	altid sådan	
foroven	altid sådan	
for resten/forresten	altid valgfrit	
for så vidt	altid sådan	
for øvrigt	altid sådan	
fra neden	altid sådan	
frem ad	med styrelse: skrives i to ord	Han trådte speederen i bund og ræsede frem ad en gade i Hanstholm.
fremad	uden styrelse: skrives i et ord	Aviser må kigge fremad.
frem for/fremfor	med styrelse: skrives valgfrit i et eller to ord	Den er spændingsstabil, robust og frem for/fremfor alt billig.
frem for/fremfor	altid valgfrit	
frem over	med styrelse: skrives i to ord	Irakerne har også den fordel at deres styrker er gravet ned i forsvarsbastioner mens de allierede skal rykke frem over åbent land.
fremover	uden styrelse: skrives i et ord	Fremover vil man på alle restauranter i Maribo kunne få mindst én kalkunret.
fremoverbøjet	altid sådan	
fuldt stop-skilt	altid sådan	
fuldt ud	altid sådan	
færdig montage	altid sådan	Han hængte billedet, en færdig montage, op inden han gik.
færdigmontage	altid sådan	Ved færdigmontage bliver karosseridele, armaturer og enkeltdele monteret på bilen.
førend	altid sådan	
første behandling	altid sådan	Efter den første behandling havde han det allerede bedre.
førstebehandling	altid sådan	Det må erkendes at der efter førstebehandlingen af regeringens forslag tegner sig et flertal.
førstegenerationsindvandrer	altid sådan	
første klasses	altid sådan	Hun sad ved siden af ham allerede på første klasses skolefoto.
førsteklasses	altid sådan	Træmøblerne er førsteklasses håndværk
først til mølle-princip	altid sådan	
ganske vist	altid sådan	
gas- og vandmester	altid sådan	
glat is	altid sådan	Banen var perfekt til curling med helt glat is.
glatis	altid sådan	Der kom de på glatis i diskussionen.
glat væk/glatvæk	altid valgfrit	
god aften	altid sådan	Han håbede at de ville få en god aften.
godaften	altid sådan	"Godaften", sagde hun og trådte tøvende et par skridt frem.
god dag	altid sådan	Det havde været en rigtig god dag for Tue.
goddag	altid sådan	Som barn øvede jeg mig på et æbletræ for at kunne sige rigtig goddag på fransk hvis jeg mødte ham.
god morgen	altid sådan	En rigtig god morgen begynder med en svømmetur.
godmorgen	altid sådan	Godmorgen, små venner, har I sovet godt?
god nat	altid sådan	Der kunne fanges op til 1000 ål på en god nat.
godnat	altid sådan	Nogle minutter tidligere havde han sagt godnat og forladt stationen i sit civile tøj.
godt nok	altid sådan	
golden delicious-æble	altid sådan	
golden retriever	altid sådan	
goodwill	altid sådan	
grandprix	altid sådan	
grundlovsdag	altid sådan	
græskkatolsk	altid sådan	
græskortodoks	altid sådan	
gud bevares/gudbevares	altid valgfrit	
gud hjælpe mig/gudhjælpemig	altid valgfrit	
gud ske lov/gudskelov	altid valgfrit	
guds velsignelse/gudsvelsignelse	altid valgfrit	
gør det selv-metode	altid sådan	
gåhjemmøde	altid sådan	
gåpåhumør	altid sådan	
gåpåmod	altid sådan	
had-kærligheds-forhold	altid sådan	
halvandenlitersflaske/halvandenliterflaske	altid valgfrit	
handout	altid sådan	
happy end	altid sådan	
haricots verts	altid sådan	
haute couture	altid sådan	
heavy metal	altid sådan	
heller ikke	altid sådan	
henad	uden styrelse: skrives i et ord	Kassereren forstod hvor det bar henad.
hen ad/henad	med styrelse: skrives valgfrit i et eller to ord	Der kom en kongeblå rygsæk marcherende hen ad/henad vejen.
hen imod/henimod	med styrelse: skrives valgfrit i et eller to ord	Det er en støtte til omstillingen hen imod/henimod demokrati og markedsøkonomi.
hen over	med styrelse: skrives i to ord	Lammene har fået et strint hen over ryggen som af en kalkkost.
hen under/henunder	med styrelse: skrives valgfrit i et eller to ord	Først hen under/henunder aften blev hverdagen for alvor anderledes.
hen ved/henved	med styrelse: skrives valgfrit i et eller to ord	Huset er hen ved/henved 250 år gammelt.
heraf	altid sådan	
her efter	med styrelse: skrives i to ord	Før valget blev der talt om 50.000 nye uddannelsespladser, men her efter valget har tallet 15.000 været nævnt.
herefter	uden styrelse: skrives i et ord	Herefter mødes patienterne én gang om måneden i et halvt år.
herefterdags	altid sådan	
herfor	altid sådan	
herforuden	altid sådan	
her fra	med styrelse: skrives i to ord	Set her fra Syd-Sverige har det allerede varet længe nok.
herfra	uden styrelse: skrives i et ord	Kandidater herfra optræder kun med års mellemrum.
herhen	altid sådan	
herhenad	altid sådan	
herhenhørende	altid sådan	
herhenimod	altid sådan	
herhenne	altid sådan	
herhennefra	altid sådan	
herhjem	altid sådan	
herhjemad	altid sådan	
herhjemme	altid sådan	
herhjemmefra	altid sådan	
her i	med styrelse: skrives i to ord	Her i Skandinavien ledes dette spild direkte ud i søerne.
heri	uden styrelse: skrives i et ord	Heri er jeg ganske eftertrykkeligt uenig.
her iblandt	med styrelse: skrives i to ord	Han befandt sig egentlig bedst her iblandt jøder, katolikker, muslimer og buddhister.
heriblandt	uden styrelse: skrives i et ord	Han besøgte mange vestlige lande, heriblandt Danmark.
herigennem	altid sådan	
herimellem	altid sådan	
her imod	med styrelse: skrives i to ord	En seks-armet stumtjener tager her imod tøjet.
herimod	uden styrelse: skrives i et ord	Herimod skal sættes at lejen for erhvervsarealet ligger på cirka det tredobbelte.
herind	altid sådan	
herindad	altid sådan	
herinde	altid sådan	
herindefra	altid sådan	
herindimellem	altid sådan	
herindomkring	altid sådan	
herindunder	altid sådan	
hermed	altid sådan	
herned	altid sådan	
hernedad	altid sådan	
hernede	altid sådan	
hernedefra	altid sådan	
hernedenfor	altid sådan	
hernedeomkring	altid sådan	
hernedomkring	altid sådan	
hernedtil	altid sådan	
hernæst	altid sådan	
herom	altid sådan	
her omkring	med styrelse: skrives i to ord	Hele området her omkring Menentela er ramt af tørke.
heromkring	uden styrelse: skrives i et ord	Der er da både sø, skov og hede heromkring.
heromme	altid sådan	
herommefra	altid sådan	
herop	altid sådan	
heropad	altid sådan	
heropomkring	altid sådan	
heroppe	altid sådan	
heroppefra	altid sådan	
heroveni	altid sådan	
herovenover	altid sådan	
her over	med styrelse: skrives i to ord	Der er højt til himlen her over det gamle hedelandskab.
herover	uden styrelse: skrives i et ord	Min søn Michael er netop flyttet herover.
heroverfor	altid sådan	
herovre	altid sådan	
herovrefra	altid sådan	
her på	med styrelse: skrives i to ord	De ældre har det generelt fint her på tærsklen til det 21. århundrede.
herpå	uden styrelse: skrives i et ord	Lad politikerne bruge deres tid og jagtinstinkter herpå.
herre gud/herregud	altid valgfrit	
her til	med styrelse: skrives i to ord	Den 45-årige mordsigtede fremstilles her til formiddag klokken 11 i grundlovsforhør.
hertil	uden styrelse: skrives i et ord	Alternativet hertil havde været at bruge de metoder som de havde afskrevet i Wien.
her til lands/hertillands	altid valgfrit	
herud	altid sådan	
herudad	altid sådan	
herudaf	altid sådan	
herude	altid sådan	
herudefra	altid sådan	
herudenfor	altid sådan	
herudeomkring	altid sådan	
herudfor	altid sådan	
herudfra	altid sådan	
herudover	altid sådan	
her under	med styrelse: skrives i to ord	Her under arbejdsbordet ligger forskellige mønter: 1-kroner, 5-kroner og 25-ører.
herunder	uden styrelse: skrives i et ord	Nogle har ligefrem dannet et netværk, herunder også nye selskaber.
her ved	med styrelse: skrives i to ord	Her ved indgangen til 90'erne ligger dansk økonomi usædvanligt lunt i svinget.
herved	uden styrelse: skrives i et ord	Herved undgår man at sejle den lange vej tilbage til Vänern.
herværende	altid sådan	
hi-fi	altid sådan	
hjem ad	med styrelse: skrives i to ord	Det var ikke bevidst at jeg valgte at køre hjem ad vejen forbi Teglholmen og H.C. Ørstedsværket.
hjemad	uden styrelse: skrives i et ord	Han vendte sig om og skyndte sig halvt løbende hjemad.
hjemme fra	med styrelse: skrives i to ord	Charlotte havde spurgt om hun ikke måtte blive hjemme fra børnehaven.
hjemmefra	uden styrelse: skrives i et ord	I dag er de to ældste børn flyttet hjemmefra.
hjemme hos-pædagog	altid sådan	
hjerte-kar-sygdom	altid sådan	
hold kæft-bolsje	altid sådan	
hole-in-one	altid sådan	
homo sapiens	altid sådan	
honoris causa	altid sådan	
hors d'oeuvre	altid sådan	
hotel garni	altid sådan	
housewarming	altid sådan	
hundekulde	altid sådan	
hvadbehager/hvabehar	altid valgfrit	
hvad enten	altid sådan	
hvad som helst	altid sådan	
hvem som helst	altid sådan	
hver anden	altid sådan	
hverandre	altid sådan	
hver gang	altid sådan	
hverken-eller	altid sådan	
hvert andet	altid sådan	
hvilken som helst	altid sådan	
hvoraf	altid sådan	
hvorefter	altid sådan	
hvorfor	altid sådan	
hvorfra	altid sådan	
hvorhen	altid sådan	
hvorhenne	altid sådan	
hvorhos	altid sådan	
hvori	altid sådan	
hvoriblandt	altid sådan	
hvorigennem	altid sådan	
hvorimellem	altid sådan	
hvorimod	altid sådan	
hvorind	altid sådan	
hvorinde	altid sådan	
hvorledes	altid sådan	
hvorlunde	altid sådan	
hvor længe	altid sådan	
hvor mange	altid sådan	
hvormed	altid sådan	
hvor meget	altid sådan	
hvornår	altid sådan	
hvorom	altid sådan	
hvoromkring	altid sådan	
hvorover	altid sådan	
hvorpå	altid sådan	
hvor som helst	altid sådan	
hvortil	altid sådan	
hvorudfra	altid sådan	
hvorunder	altid sådan	
hvorved	altid sådan	
hvor vidt	med styrelse: skrives i to ord	På mødet skal vi vurdere hvor vidt det er kommet med mobningen i klassen.
hvorvidt	uden styrelse: skrives i et ord	Angiveligt skal de strides om, hvorvidt Tyskland kan forblive i Atlantpagten.
i aften	altid sådan	
i aftes	altid sådan	
i alt	altid sådan	
iblandt	altid sådan	
i dag	altid sådan	
i det	med styrelse: skrives i to ord	Angela Merkel er vokset op i det gamle DDR.
idet	uden styrelse: skrives i et ord	Byggeriet kunne gå i gang med det samme, idet byggelovgivningen er forudsat opfyldt.
i fjor	altid sådan	
i forh. til/ift. (fork. for i forhold til)	altid valgfrit	
i færd med	altid sådan	
ifølge, forkortes if.	altid sådan	
i gang	altid sådan	
igangsætte	altid sådan	
i går	altid sådan	
i henh. til/iht. (fork. for i henhold til)	altid valgfrit	
i hvert fald	altid sådan	
ikke desto mindre	altid sådan	
ikke engang	altid sådan	
i land	altid sådan	
ilandbringe	altid sådan	
ilandsætte	altid sådan	
imellem	altid sådan	
imens/imedens	altid valgfrit	
immer hen	altid sådan	
immer væk/immervæk	altid valgfrit	
imod	altid sådan	
i morgen	altid sådan	
i morges	altid sådan	
in absentia	altid sådan	
in absurdum	altid sådan	
i nat	altid sådan	
in blanco	altid sådan	
in casu	altid sådan	
ind ad	med styrelse: skrives i to ord	Så går Glistrup ind ad døren.
indad	uden styrelse: skrives i et ord	Bagbenene må ikke dreje indad, og forbenene skal være parallelle.
inde fra	med styrelse: skrives i to ord	Der hørtes ikke en lyd inde fra lejligheden.
indefra	uden styrelse: skrives i et ord	Det må kaldes frem indefra.
ind efter	med styrelse: skrives i to ord	Ældrebyrden sætter først for alvor ind efter 2010.
indefter	uden styrelse: skrives i et ord	Månerne bevæger sig udefter, og ringene bevæger sig indefter.
inde i	altid sådan	
inden borde	altid sådan	
inden døre	altid sådan	
indendørs	altid sådan	
indenfor	uden styrelse: skrives i et ord	Da vi kom indenfor, så der herrens ud.
inden for/indenfor	med styrelse: skrives valgfrit i et eller to ord	Inden for/indenfor det næste år forventer vi afgørende resultater.
indeni	uden styrelse: skrives i et ord	Vi går rundt og er glade indeni hele dagen.
inden i/indeni	med styrelse: skrives valgfrit i et eller to ord	Han krøllede bogstaverne sammen og lagde dem inden i/indeni avisen.
indenom	uden styrelse: skrives i et ord	Tiden vil vise om de ikke igen overhaler os indenom.
inden om/indenom	med styrelse: skrives valgfrit i et eller to ord	Makrellen var et smut inden om/indenom vore farvande for en lille måned siden.
indenunder	uden styrelse: skrives i et ord	Hun havde en tynd, rød vindjakke på og vist allerhøjst en hvid T-shirt indenunder.
inden under/indenunder	med styrelse: skrives valgfrit i et eller to ord	Inden under/indenunder frakken har man patenstrik i bølgerib.
inde under	altid sådan	
ind i	altid sådan	
ind imellem	med styrelse: skrives i to ord	Stik citronskiver ind imellem nogle af kødstykkerne.
indimellem	uden styrelse: skrives i et ord	Han har indimellem et voldsomt og ustyrligt temperament.
ind over	med styrelse: skrives i to ord	Denne billedstorm vælter ind over de unge.
indover	uden styrelse: skrives i et ord	En manager kom også ret hurtigt indover for at styre gassernes fremtid.
ind til	med styrelse: skrives i to ord	Dengang gik havet helt ind til byen.
indtil	uden styrelse: skrives i et ord	Bagagerummet ser flot og velordnet ud indtil man begynder at læsse bagagen ind.
ind under	med styrelse: skrives i to ord	Han så faren og kravlede ind under sengen.
indunder	uden styrelse: skrives i et ord	Tag trøjen indunder.
in duplo	altid sådan	
in effigie	altid sådan	
in extenso	altid sådan	
ingenlunde	altid sådan	
ingenmandsland	altid sådan	
ingen sinde/ingensinde	altid valgfrit	
ingen som helst	altid sådan	
ingen steder	altid sådan	
ingensteds/intetsteds	altid valgfrit	
ingen ting/ingenting	altid valgfrit	
ingen vegne	altid sådan	
in medias res	altid sådan	
in memoriam	altid sådan	
in mente/i mente	altid valgfrit	
in natura	altid sådan	
in persona	altid sådan	
in plano	altid sådan	
in pleno	altid sådan	
insiderhandel	altid sådan	
in solidum	altid sådan	
in spe	altid sådan	
intercitytog	altid sådan	
intet som helst	altid sådan	
in triplo	altid sådan	
in vitro-befrugtning	altid sådan	
i orden	altid sådan	
i overmorgen	altid sådan	
i sinde	altid sådan	
i stand til	altid sådan	
i stedet for	altid sådan	
i stykker	altid sådan	
i stå	altid sådan	
itu	altid sådan	
i øvrigt	altid sådan	
i år	altid sådan	
ja tak	altid sådan	
joint venture	altid sådan	
joint venture-basis	altid sådan	
jord til jord-missil	altid sådan	
jord til luft-missil	altid sådan	
jo tak	altid sådan	
junkfood	altid sådan	
junkmail	altid sådan	
jus practicandi	altid sådan	
jævnt hen	altid sådan	
kaffeslabberas	altid sådan	
keyaccountmanager	altid sådan	
kickoff	altid sådan	
kickoffmøde	altid sådan	
klos hold/kloshold	altid valgfrit	
knockout	altid sådan	
knowhow	altid sådan	
kraft-varme-værk	altid sådan	
krydsogtværs (’krydsord’)	altid sådan	
kryds og tværs (på kryds og tværs)	altid sådan	
kæmpestor	altid sådan	
køb og smid væk-mentalitet	altid sådan	
kør selv-ferie	altid sådan	
laisser faire-politik/laissez faire-politik	altid valgfrit	
langs ad	med styrelse: skrives i to ord	Træet slibes på langs ad årerne og støves af.
langsad	uden styrelse: skrives i et ord	Det ordner vi langsad.
langs med	altid sådan	
langt fra	med styrelse: skrives i to ord	Der er langt fra ord til handling.
langtfra	uden styrelse: skrives i et ord	Det er langtfra tilfældet.
lapis lazuli	altid sådan	
layout	altid sådan	
lige for	med styrelse: skrives i to ord	Det ligger lige for fødderne af os.
ligefor	uden styrelse: skrives i et ord	Løsningen ligger ligefor.
lige frem	med styrelse: skrives i to ord	Den leder lige frem til katastrofen.
ligefrem	uden styrelse: skrives i et ord	Nogle har ligefrem dannet et netværk, herunder også nye selskaber.
lige meget	altid sådan	
lige på	altid sådan	
lige som	med styrelse: skrives i to ord	Stregen er helt lige som hvis hun havde brugt en lineal.
ligesom	uden styrelse: skrives i et ord	Vantro opdagede hun at hun ligesom følte sig helt glad.
lige straks	altid sådan	
lige så	med styrelse: skrives i to ord	Alligevel handler bogen lige så meget om dig og mig som om fremtidens supermennesker.
ligeså	uden styrelse: skrives i et ord	Kødet var halvtrist og saucen ligeså.
lige til	med styrelse: skrives i to ord	Faktisk gennemførte han komediespillet lige til sin død.
ligetil	uden styrelse: skrives i et ord	Analogien er smuk og ligetil.
lige ud	med styrelse: skrives i to ord	Det er rock og rul lige ud ad landevejen med hvinende dæk og benzin i blodet.
ligeud	uden styrelse: skrives i et ord	Det blev sagt ligeud.
lige ved	med styrelse: skrives i to ord	Det er lige ved at være groft.
ligeved	uden styrelse: skrives i et ord	Vi vandt ikke, men det var ligeved.
lille bitte/lillebitte	altid valgfrit	
lille by	altid sådan	Jeg synes faktisk at Haslev er en ret lille by.
lilleby	altid sådan	Mordet fandt sted nær den støvede lilleby Falls City.
lille juleaften	altid sådan	Vi besluttede at holde en lille juleaften i år uden mine søskende (dvs. d. 24. dec.).
lille juleaften/lillejuleaften	altid valgfrit	Vi besluttede at holde lillejuleaften/lille juleaften i år uden mine søskende (dvs. d. 23. dec.).
lille skole	altid sådan	Hér har vi fordele af at vi er en lille skole.
lilleskole	altid sådan	Sådan husker Jacob på ni år skiftet fra en københavnsk folkeskole til en midtjysk lilleskole.
lit de parade	altid sådan	
lockout	altid sådan	
log-in/login	altid valgfrit	
lookalike	altid sådan	
luft til jord-raket	altid sådan	
læbe-gane-spalte	altid sådan	
længe nok	altid sådan	
længe siden	altid sådan	
makeup	altid sådan	
medmindre	altid sådan	
memento mori	altid sådan	
midt for	med styrelse: skrives i to ord	Jeg blev anbragt midt for en væg.
midtfor	uden styrelse: skrives i et ord	"Kan jeg få to pladser midtfor, første række", siger han.
midt i	med styrelse: skrives i to ord	Hun var netop brudt sammen midt i hans program.
midti	uden styrelse: skrives i et ord	Men måske lå der lidt vand endnu på bunden inde midti.
midt imellem	med styrelse: skrives i to ord	Inde i koncertsalen, midt imellem de sirligste modedamer.
midtimellem	uden styrelse: skrives i et ord	Jeg tror nok at tallet skal findes måske lidt midtimellem.
midt over	med styrelse: skrives i to ord	Dette skal altid foregå midt over en gulvbjælke.
midtover	uden styrelse: skrives i et ord	Da han i raseri knækkede sin ketsjer midtover.
midt på	med styrelse: skrives i to ord	En hellig ko går midt på vejen.
midtpå	uden styrelse: skrives i et ord	En lille hvid firkant dukker op midtpå og toner langsomt ud.
minsandten	altid sådan	
minsæl	altid sådan	
missing link	altid sådan	
mixed double	altid sådan	
mixed grill	altid sådan	
mund- og klovesyge/mund- og klovsyge	altid valgfrit	
mund til mund-metode	altid sådan	
mund til næse-metode	altid sådan	
måneds tid	altid sådan	
nature morte	altid sådan	
nebengesjæft	altid sådan	
ned ad	med styrelse: skrives i to ord	De tog hinanden i hånden og gik ned ad deres havegang.
nedad	uden styrelse: skrives i et ord	Vejen skrånede nedad, og hun satte farten op.
ned af	altid sådan	
nede fra	med styrelse: skrives i to ord	Lige da jeg kom hjem nede fra engen, så jeg at de trak mor og far ind.
nedefra	uden styrelse: skrives i et ord	Det er et eksempel på styring nedefra.
ned efter	med styrelse: skrives i to ord	Han gik ned efter cigaretpapir, og da han kom tilbage manglede der en klump hash.
nedefter	uden styrelse: skrives i et ord	Lad rouladen ligge indpakket med sammenføjningen nedefter til den er helt kold.
nede i	altid sådan	
nedenfor	uden styrelse: skrives i et ord	Nedenfor redegøres for en af de første produktionsgodkendelser fra den amerikanske miljøstyrelse.
neden for/nedenfor	med styrelse: skrives valgfrit i et eller to ord	De er efter lidt tilvænning sat ud i bagvandet neden for/nedenfor turbinen ved kraftværket.
nedenom	uden styrelse: skrives i et ord	I London f.eks. er små 20 studier gået nedenom og hjem.
neden om/nedenom	med styrelse: skrives valgfrit i et eller to ord	Han fortsatte sin sædvanlige omvej neden om/nedenom havnen.
nedenunder	uden styrelse: skrives i et ord	Et par baroktøser giver op og går nedenunder for at danse hip hop i stedet.
neden under/nedenunder	med styrelse: skrives valgfrit i et eller to ord	Neden under/Nedenunder os lå byen.
nede om	altid sådan	
nede under	altid sådan	
ned fra	altid sådan	
ned i	altid sådan	
ned om	med styrelse: skrives i to ord	Pak dobbelt folie godt ned om kanten på fadet og stil det i ovnen ved 200 grader i ca. halvanden time.
nedom	uden styrelse: skrives i et ord	Og bliver jeg mon ikke bred nedom, hvis jeg hver dag skal sidde stille så længe?
ned over	med styrelse: skrives i to ord	Han lod igen øjnene løbe ned over spisekortet.
nedover	uden styrelse: skrives i et ord	Nu er floden rigtig stærk, og vi bliver revet med af strømmen nedover.
negro spiritual	altid sådan	
nej tak	altid sådan	
new age	altid sådan	
new age-musik	altid sådan	
nogenledes	altid sådan	
nogenlunde	altid sådan	
nogen sinde/nogensinde	altid valgfrit	
nogen som helst	altid sådan	
nogen vegne	altid sådan	
noget som helst	altid sådan	
nok en gang	altid sådan	
no name-produkt	altid sådan	
nonstop	altid sådan	
non troppo	altid sådan	
norden om	med styrelse: skrives i to ord	Først op gennem Kattegat og Skagerak, norden om Skotland og ud i Atlanterhavet.
nordenom	uden styrelse: skrives i et ord	Jeg er slet ikke tryg ved at han sejler nordenom.
nord om	med styrelse: skrives i to ord	Maskinen var kommet nord om de to slanke broer over det himmelblå Lillebælt.
nordom	uden styrelse: skrives i et ord	Den bakke går vi altså nordom.
notarius publicus	altid sådan	
nu om stunder	altid sådan	
nu til dags	altid sådan	
nær på	med styrelse: skrives i to ord	De fine ord om beslutninger så nær på borgerne som muligt skal gives reelt indhold.
nærpå	uden styrelse: skrives i et ord	Et par stykker blev dog bange for den når den kom helt nærpå og gav sig til at græde.
nær ved	med styrelse: skrives i to ord	Hun havde aldrig før været nær ved en levende fisk.
nærved	uden styrelse: skrives i et ord	Nærved i en gårdhave ligger 10 lig.
næst efter	med styrelse: skrives i to ord	Næst efter enkelte koryfæer er paternosteren Folketingets største attraktion.
næstefter	uden styrelse: skrives i et ord	Hvem kom så næstefter?
nå ja	altid sådan	
når som helst	altid sådan	
offline	altid sådan	
offside	altid sådan	
om bord/ombord	altid valgfrit	
om end/omend	altid valgfrit	
om kap	altid sådan	
omkuld	altid sådan	
om lidt	altid sådan	
onemanshow	altid sådan	
on location	altid sådan	
op ad	med styrelse: skrives i to ord	Drengene gik op ad en trappe til en lejlighed på første sal.
opad	uden styrelse: skrives i et ord	Det er lidt vanskeligere når man skal opad.
open source	altid sådan	
op over	med styrelse: skrives i to ord	De to discount-færger Ask og Urd er belånt til op over mastetoppen for tilsammen 400 millioner kroner.
opover	uden styrelse: skrives i et ord	Og så pilede vi som bavianer opover, ind over klipperne for at finde et læsted.
oppe fra	med styrelse: skrives i to ord	Hingstenes vrinsken skar gennem larmen oppe fra hestemarkedet.
oppefra	uden styrelse: skrives i et ord	Det er styring oppefra.
oppe imod	altid sådan	
oppe mod	altid sådan	
op til	med styrelse: skrives i to ord	Man skal op til landsbyen for at gøre indkøb.
optil	uden styrelse: skrives i et ord	Buskene er tættest optil.
ovenanført	altid sådan	
ovenfor	uden styrelse: skrives i et ord	Kog risene i 4,5 dl kogende vand og 1 tsk. salt som beskrevet ovenfor.
oven for/ovenfor	med styrelse: skrives valgfrit i et eller to ord	Nederdelen slutter lidt oven for/ovenfor knæet.
ovenforstående	altid sådan	
ovenfra	altid sådan	
oveni	uden styrelse: skrives i et ord	Herefter lægges der ca. 3.000 kr. oveni.
oven i/oveni	med styrelse: skrives valgfrit i et eller to ord	Giver firmaerne pæne overskud, får de ansatte oven i/oveni den aftalte faste løn en klækkelig bonus.
ovenikøbet	altid sådan	
ovenind	altid sådan	
ovennævnt	altid sådan	
ovenom	uden styrelse: skrives i et ord	Her går vi altid ovenom, så slipper vi for mudderet.
oven om/ovenom	med styrelse: skrives valgfrit i et eller to ord	De kørte oven om/ovenom byen.
ovenomtalt	altid sådan	
ovenover	uden styrelse: skrives i et ord	Hvis indskuddet mindskes, forstærkes støj af trin m.v. fra etagen ovenover.
oven over/ovenover	med styrelse: skrives valgfrit i et eller to ord	Oven over/Ovenover ham så himlen ud som en motorvej i myldretiden.
ovenpå	uden styrelse: skrives i et ord	Man erkender at Venstre i øjeblikket er ovenpå.
oven på/ovenpå	med styrelse: skrives valgfrit i et eller to ord	Lige inden serveringen placeres rejerne oven på/ovenpå det øvrige.
oven senge	altid sådan	
ovenstående	altid sådan	
oventil	altid sådan	
ovenud	altid sådan	
oven vande	altid sådan	
overall	altid sådan	
over alt	med styrelse: skrives i to ord	Jeg elsker min far over alt på Jorden.
overalt	uden styrelse: skrives i et ord	Overalt er der kælet for detaljerne.
over bord	altid sådan	
over ende	altid sådan	
overens	altid sådan	
overfor	uden styrelse: skrives i et ord	Men pludselig sad hun i stolen overfor.
over for/overfor	med styrelse: skrives valgfrit i et eller to ord	Over for/Overfor journalister kan han være dræbende ironisk.
over hovedet	med styrelse: skrives i to ord	Nu vokser det os over hovedet.
overhovedet	uden styrelse: skrives i et ord	Kan man overhovedet forhindre at det sker igen?
over kors	altid sådan	
over styr	altid sådan	
par avion	altid sådan	
par excellence	altid sådan	
pas de deux	altid sådan	
password	altid sådan	
patchwork	altid sådan	
pater familias	altid sådan	
penthouselejlighed	altid sådan	
perpetuum mobile	altid sådan	
persona grata	altid sådan	
persona non grata	altid sådan	
pickup	altid sådan	
pil selv-reje	altid sådan	
pinup	altid sådan	
pomme frite/pomfrit	altid valgfrit	
pop op-bog	altid sådan	
pop op-vindue	altid sådan	
port salut	altid sådan	
poste restante	altid sådan	
poste restante-brev	altid sådan	
post festum	altid sådan	
postillon d'amour	altid sådan	
primus motor	altid sådan	
pro anno	altid sådan	
pro et contra	altid sådan	
proforma	altid sådan	
pro persona	altid sådan	
pro rata	altid sådan	
pro rata-hæftelse	altid sådan	
public domain	altid sådan	
public domain-program	altid sådan	
public relation	altid sådan	
public relation-afdeling/public relations-afdeling	altid valgfrit	
public service	altid sådan	
public service-kanal	altid sådan	
på grund af	altid sådan	
på ny	altid sådan	
quiche lorraine	altid sådan	
rask væk/raskvæk	altid valgfrit	
rector magnificus	altid sådan	
rigtignok	altid sådan	Men forholdene var rigtignok anderledes da jeg tog eksamen i 1985.
rigtig nok el. rigtigt nok (se også T-leksikonet)	altid sådan	Han vendte sig om, og fornemmelsen viste sig at være rigtig nok.
risalamande	altid sådan	
rock and roll	altid sådan	
rock and roll-band	altid sådan	
roll-on/rollon	altid valgfrit	
rundt om	med styrelse: skrives i to ord	Vor egen tids historie lurer rundt om alle hjørner.
rundtom	uden styrelse: skrives i et ord	Hist og her stod der små klatter med grantræer, og rundtom lå der sommerhuse.
rundt omkring	med styrelse: skrives i to ord	Elektronen bevæger sig rundt omkring atomets kerne med en hastighed, der kunne bringe den 8 gange jorden rundt på ét sekund.
rundtomkring	uden styrelse: skrives i et ord	Der er alt for mange tekniske standarder rundtomkring i Europa.
sans comparaison	altid sådan	
science fiction	altid sådan	
science fiction-roman	altid sådan	
selv om/selvom	altid valgfrit	
selv samme/selvsamme	altid valgfrit	
selv tak	altid sådan	
senere hen	altid sådan	
serviceminded	altid sådan	
siden hen/sidenhen	altid valgfrit	
simpelt hen/simpelthen	altid valgfrit	
sit-in/sitin	altid valgfrit	
sleep-in/sleepin	altid valgfrit	
slet ikke	altid sådan	
slå om-nederdel	altid sådan	
slå ud-melding	altid sådan	
smadderærgerligt	altid sådan	
smalltalk	altid sådan	
små bitte	altid sådan	
snabel-a	altid sådan	
snotforkølet	altid sådan	
softice	altid sådan	
solar plexus	altid sådan	
som helst	altid sådan	
somme tider/sommetider	altid valgfrit	
som om	altid sådan	
sort-hvid	altid sådan	
sparto (sige sparto)	altid sådan	
spar to (spillekortet)	altid sådan	
spin-off	altid sådan	
stadig væk/stadigvæk	altid valgfrit	
stand-in/standin	altid valgfrit	
standup	altid sådan	
standupcomedy	altid sådan	
standupkomiker	altid sådan	
standupper	altid sådan	
status quo	altid sådan	
store bededag	altid sådan	
stor magt	altid sådan	Skulle jeg besidde så stor magt?
stormagt	altid sådan	Frankrig har været en stormagt.
stort set	altid sådan	
summa summarum	altid sådan	
superlækkert	altid sådan	
swimmingpool	altid sådan	
syd om	med styrelse: skrives i to ord	Man skulle syd om Afrika til Bombay.
sydom	uden styrelse: skrives i et ord	Vinden drejede sydom.
syns- og skønsmand	altid sådan	
sønden om	med styrelse: skrives i to ord	Trods alt var det nemmere at sejle sønden om Sydamerika eller Afrika.
søndenom	uden styrelse: skrives i et ord	Vinden drejede søndenom.
såfremt	altid sådan	
så længe	altid sådan	
såmænd	altid sådan	
så snart	altid sådan	
såsom	altid sådan	
så vel som/såvel som	altid valgfrit	
så vidt	altid sådan	
tag selv-bord	altid sådan	
take-off	altid sådan	
tast selv-service	altid sådan	
teamwork	altid sådan	
tekst-tv/tekst-TV	altid valgfrit	
tete-a-tete	altid sådan	
thousand island-dressing	altid sådan	
tids nok/tidsnok	altid valgfrit	
tik tak	altid sådan	
til dels	altid sådan	
til fælles/tilfælles	altid valgfrit	
til gode	altid sådan	
til grunde	altid sådan	
til højre	altid sådan	
til kende	altid sådan	
til lands	altid sådan	
til leje	altid sådan	
tillige	altid sådan	
tillige med	med styrelse: skrives i to ord	Den utrolig høje temperatur tillige med den seismiske aktivitet, målt dernede, har givet alverdens ingeniører nye problemer at tumle med.
tilligemed	uden styrelse: skrives i et ord	Hvis sygeplejersken så tilligemed er træt og uoplagt, er det vanskeligere at mobilisere kræfter til situationsforståelsen.
til lykke/tillykke	altid valgfrit	
til låns	altid sådan	
til med	med styrelse: skrives i to ord	Pisk 1 1/2 dl piskefløde i, og smag til med salt og peber.
tilmed	uden styrelse: skrives i et ord	I Norge har man tilmed bedt mig om at levere buketter af korn.
til mode	altid sådan	
til og fra-kort	altid sådan	
tilovers	altid sådan	
tilsammen	altid sådan	
til sidst	altid sådan	
til stede	altid sådan	
til venstre	altid sådan	
timeout	altid sådan	
times tid	altid sådan	
topersoners	altid sådan	
tour de force	altid sådan	
tredjegenerationsindvandrer	altid sådan	
trip trap	altid sådan	
tro og love-erklæring	altid sådan	
tur og retur/tur-retur	altid valgfrit	
tvært imod	med styrelse: skrives i to ord	Det er tvært imod mangfoldigheden.
tværtimod	uden styrelse: skrives i et ord	Tværtimod bør lønningerne sættes ned hvis konkurrenceevnen blot skal bevares uændret.
tænd og sluk-ur	altid sådan	
ud af	altid sådan	
ude af	altid sådan	
ude for	altid sådan	
ude fra	med styrelse: skrives i to ord	Jeg tror det har hjulpet at garnene skal være 100 m ude fra kysten.
udefra	uden styrelse: skrives i et ord	Selv udefra og i hård frost stinker huset ubeskriveligt.
ud efter	med styrelse: skrives i to ord	Han erkendte at have sparket ud efter malersvenden.
udefter	uden styrelse: skrives i et ord	Ri de tre lag sammen, start i midten, og ri udefter.
udenad	altid sådan	
udenfor	uden styrelse: skrives i et ord	Vi bad om et bord udenfor og fik at vide at vi kunne sætte os hvor som helst.
uden for/udenfor	med styrelse: skrives valgfrit i et eller to ord	Han ryger efter alt at dømme helt uden for/udenfor døren når udvalget mødes i fremtiden.
udenom	uden styrelse: skrives i et ord	Der er ingen vej udenom.
uden om/udenom	med styrelse: skrives valgfrit i et eller to ord	Jeg kunne ikke se nogen vej uden om/udenom skyldkomplekserne.
udenomssnak	altid sådan	
udenover	uden styrelse: skrives i et ord	Tag en skjorte udenover.
uden over/udenover	med styrelse: skrives valgfrit i et eller to ord	Påklædningen er lig en fattig russers, de gule sokker uden over/udenover bukserne.
udenpå	uden styrelse: skrives i et ord	Har man det godt indeni, har man det også udenpå.
uden på/udenpå	med styrelse: skrives valgfrit i et eller to ord	Nerverne sidder uden på/udenpå tøjet.
uden videre	altid sådan	
ude omkring	altid sådan	
ud for	altid sådan	
udover	uden styrelse: skrives i et ord	Skibet tog kurs udover.
ud over/udover	med styrelse: skrives valgfrit i et eller to ord	Ud over/Udover de almindelige lavkonjunkturer i samfundet er der en del andre årsager.
ud til bens	altid sådan	
uges tid	altid sådan	
underhånden	altid sådan	
update	altid sådan	
up to date	altid sådan	
ved hjælp af	altid sådan	
ved lige	altid sådan	
vedligeholde	altid sådan	
vel at mærke	altid sådan	
velbekomme	altid sådan	
vel nok	altid sådan	
vel sagtens	altid sådan	Han frygtede ikke sit eget otium, for han havde mange interesser, og så kan man vel sagtens klare sig.
velsagtens	altid sådan	Censor roder med nogle papirer, velsagtens for at give en kompetent facade.
vel tilfreds	altid sådan	Poul fik solgt tomaterne til en bedre pris end I gættede på. Det er du vel tilfreds med.
veltilfreds	altid sådan	Roy nikker veltilfreds og skuer op mod himlen.
vel tilpas	altid sådan	Når tallet er steget igen, så er det vel tilpas normalt til at han kan komme hjem.
veltilpas	altid sådan	Dertil kommer at han ser overordentlig veltilpas ud.
vel vidende	altid sådan	
vesten om	med styrelse: skrives i to ord	Han gik vesten om byen.
vestenom	uden styrelse: skrives i et ord	Vinden drejede vestenom.
vest om	med styrelse: skrives i to ord	Disse forslag kan suppleres med en forlæggelse af Harrestrupvej vest om Lystoftegård.
vestom	uden styrelse: skrives i et ord	Vinden drejede vestom.
vice versa	altid sådan	
viden fra	altid sådan	
viden om	altid sådan	
viderekomne	altid sådan	
viola da gamba	altid sådan	
virtual reality	altid sådan	
vis-a-vis	altid sådan	
vist nok	altid sådan	De fik en stemmefremgang på otte pct., og det var vist nok til at partiet fik absolut flertal i Kiel dengang.
vistnok	altid sådan	Han startede sin vogn, vistnok en Alfa Romeo.
von hørensagen	altid sådan	
vugge til grav-princip	altid sådan	
væg til væg-tæppe	altid sådan	
værsartig/vær så artig	altid valgfrit	
værsgo/vær så god	altid valgfrit	
walkie-talkie	altid sådan	
webshop	altid sådan	
whitewaterrafting	altid sådan	
widescreen	altid sådan	
workout	altid sådan	
workshop	altid sådan	
yorkshireterrier	altid sådan	
ærkereaktionær	altid sådan	
ødipuskompleks	altid sådan	
øre-næse-hals-læge	altid sådan	
østen om	med styrelse: skrives i to ord	Vi bærer plantagens duft af kryddernelliker med os, da vi går østen om Dar-Es-Salam med alle sejl sat.
østenom	uden styrelse: skrives i et ord	Vinden drejede østenom.
øst om	med styrelse: skrives i to ord	Hun sejlede øst om øen.
østom	uden styrelse: skrives i et ord	Vinden drejede østom.
åbent hus-arrangement	altid sådan	
åh ja	altid sådan	
åh nej	altid sådan"""

candidates = [t.split("\t")[0] for t in text.split("\n")]
candidates = [
    c for c in candidates if c not in sammensatte_ord and len(c.split(" ")) == 1
]
# print("\n".join(candidates))
# copy and paste in:
# tagged similar to above:

additional_words = """action|film
afsted|komme
aha|oplevelse
aller|bedst
all|round
al|ting
back|up
bag|efter
bag|i
bag|om
bag|over
bag|på
bag|ud
bag|ude
bag|ved
bitte|lille
bitte|små
black|out
bokser|shorts
bungee|jumping
center|forward
check|in
come|back
cover|up
dansk|amerikaner
den|gang
der|efter
der|fra
der|hen
der&hen|ad
der&hen|hørende
der&hen|imod
der|henne
der&henne|fra
der|hjem
der|hjem&ad
der|hjemme
der|hjemme|fra
der|hos
der|i
der&i|blandt
der&i|gennem
der&i|mellem
der&i|mod
der|ind
der|indad
der|inde
der|inde|fra
derind|imellem
der|ind|omkring
der|ind|under
der|med
der|ned
der|ned&ad
der|nede
der&nede|fra
der|neden|for
der|nede|omkring
der|ned|omkring
der|ned|til
der|næst
der|om
der|omkring
der|omme
der|omme|fra
der|op
der|op|ad
der|op|omkring
der|oppe
der|oppe|fra
der|oven|i
der|oven|over
der|over
der|over|for
der|ovre
der|ovre|fra
der|på
der|som
der|steds
der|til
der|til&hørende
der|ud
der|ud|ad
der|ud|af
der|ude
der|ude|fra
der|uden|for
der|ude|omkring
der|ud|for
der|ud|fra
der|ud|over
der|under
der|ved
des|værre
drive|-|in
drive|in
drop|out
dødsen|s|farlig
død|træt
efter|som
en|gang
et|værelses
et|års
faktura|dato
feed|back
fifty|-|fifty
follow|up
for|neden
for|oven
frem|ad
frem|over
frem|over|bøjet
færdig|montage
førend
første|behandling
første|generation|s|indvandrer
første|klasses
glat|is
god|aften
god|dag
god|morgen
god|nat
good|will
grand|prix
grund|lov&s&dag
græsk|katolsk
græsk|ortodoks
gå|hjem|møde
gå|på|humør
gå|på|mod
had|-|kærligheds|-|forhold
halv&anden|liter|s|flaske
halv&anden|liter|flaske
hand|out
hen|ad
her|af
her|efter
her|efter|dags
her|for
her|for|uden
her|fra
her|hen
her|hen|ad
her|hen|hørende
her|hen|imod
her|henne
her|henne|fra
her|hjem
her|hjem&ad
her|hjemme
her|hjemme&fra
her|i
her|i|blandt
her|i|gennem
her|i|mellem
her|i|mod
her|ind
her|ind&ad
her|inde
her|inde|fra
her|ind|imellem
her|ind|omkring
her|ind|under
her|med
her|ned
her|ned|ad
her|nede
her|nede|fra
her|neden|for
her|nede|omkring
her|ned|omkring
her|ned|til
her|næst
her|om
her|omkring
her|omme
her|omme|fra
her|op
her|opad
her&op|om&kring
her|oppe
her|oppe|fra
her|oveni
her|oven|over
her|over
her|over|for
her|ovre
her|ovre|fra
her|på
her|til
her|ud
her|ud|ad
her|ud|af
her|ude
her|ude|fra
her|uden|for
her|ude|omkring
her|ud|for
her|ud|fra
her|ud|over
her|under
her|ved
her|værende
hi|-|fi
hjem|ad
hjemme|fra
hjerte|-|kar|-|sygdom
hole|-|in|-|one
house|warming
hunde|kulde
hvad|behager
hva|behar
hver|andre
hverken|-|eller
hvor|af
hvor|efter
hvor|for
hvor|fra
hvor|hen
hvor|henne
hvor|hos
hvor|i
hvor|i|blandt
hvor|i|gennem
hvor|i|mellem
hvor|i|mod
hvor|ind
hvor|inde
hvor|ledes
hvor|lunde
hvor|med
hvor|når
hvor|om
hvor|om|kring
hvor|over
hvor|på
hvor|til
hvor|ud|fra
hvor|under
hvor|ved
hvor|vidt
i|blandt
i|det
i|gang&sætte
i|land|bringe
i|land|sætte
i|mellem
i|mens
i|medens
i|mod
ind|ad
inde|fra
ind|efter
inden|dørs
inden|for
inden|i
inden|om
inden|under
ind|i|mellem
ind|over
ind|til
ind|under
ingen|lunde
ingen|mand|s|land
ingen|steds
intet|steds
insider|handel
inter&city|tog
i|tu
junk|food
junk|mail
kaffe|slabberas
kaffe|slabberads
key|account|manager
kick|off
kick&off|møde
knock|out
know|how
kraft|-|varme|-|værk
kæmpe|stor
lang|sad
langt|fra
lay|out
lige|for
lige|frem
lige|som
lige|så
lige|til
lige|ud
lige|ved
lill|eby
lille|skole
lock|out
log|-|in
log|in
look|alike
læbe|-|gane|-|spalte
make|up
med|mindre
midt|for
midt|i
midt|i|mellem
midt|over
midt|på
min|sandten
min|sæl
neben|gesjæft
ned|ad
nede|fra
ned|efter
neden|for
neden|om
neden|under
ned|om
ned|over
nogen|ledes
nogen|lunde
non|stop
norden|om
nord|om
nær|på
nær|ved
næst|efter
off|line
off|side
om|kuld
one|man|show
op|ad
op|over
oppe|fra
op|til
oven|an|ført
oven|for
oven|forstående
oven|fra
oven|i
oven|i|købet
oven|ind
oven|nævnt
oven|om
oven|omtalt
oven|over
oven|på
oven|stående
oven|til
oven|ud
over|all
over|alt
over|ens
over|for
over|hovedet
pass|word
patch|work
pent&house|lejlighed
pick|up
pin|up
pro|forma
rigtig|nok
ris|a|la|mande
roll|-|on
roll|on
rundt|om
rundt|om|kring
service|minded
sit|-|in
sit|in
sleep|-|in
sleep|in
smadder|ærgerligt
small|talk
snabel|-|a
snot|for&kølet
soft|ice
sort|-|hvid
spin|-|off
stand|-|in
stand|in
stand|up
stand&up|comedy
stand&up|komiker
stand|upper
stor|magt
super|lækkert
swimming|pool
syd|om
sønden|om
så|fremt
så|mænd
så|som
take|-|off
team|work
tekst|-|tv
tekst|-|TV
tete|-|a|-|tete
til|lige
til|lige|med
til|med
til|overs
til|sammen
time|out
to|personers
tredje|generation|s|indvandrer
tvært|imod
ude|fra
ud|efter
uden|ad
uden|for
uden|om
uden|om|s|snak
uden|over
uden|på
ud|over
under|hånden
up|date
vedlige|holde
vel|bekomme
vel|sagtens
vel|tilfreds
vel|til&pas
vesten|om
vest|om
videre|komne
vis|-|a|-|vis
vist|nok
walkie|-|talkie
web|shop
white|water|rafting
wide|screen
work|out
work|shop
york&shire|terrier
ærke|reaktionær
ødipus|kompleks
øre|-|næse|-|hals|-|læge
østen|om
øst|om"""


orddele = [
    [compound.split("&") for compound in word.split("|")]
    for word in additional_words.split("\n")
]


sammensatte_ord2 = {
    "".join([subc for compound in ord for subc in compound]): ord for ord in orddele
}

sammensatte_ord.update(sammensatte_ord2)
len(sammensatte_ord)
