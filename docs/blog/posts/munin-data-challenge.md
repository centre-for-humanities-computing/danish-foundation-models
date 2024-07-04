---
draft: false
date: 2024-01-11
---

# Data er afgørende
Sprogmodeller trænes på store mænger af data. De data man træner på udgør fundamentet for sprogmodellerne, og hvad de kan bruges til. Generelt er tilgangen at jo mere data, jo bedre bliver modellel, men der er mange detaljer der udgør et gode datasæt.

## Det er ikke simpelt
Der er mange tekniske spørgsmål omkring data, som er svære at svare på. Vi ved, at enorme mængder af data er nødvendige for at træne en god model. Det er et åbent spørgsmål hvor meget data der skal til, og af hvilken slags og kvalitet, for få en sprogmodel som være god til dansk.

Det er en åbent research sprøgsmål, hvor meget data der skal til for at træne en sprogmodel. Grundet til at det er et åbent sprøgsmål er at det afhænger af rigtig mange faktore, bl.a., hvilken use-case sprogmodellel skal bruges til.

Et spørgsmål vedrører mængden af data og indholdet deraf på dansk. Et andet spørgsmål vedrører andre naturlige sprog eller andre former for tekstuelle data, som f.eks. kode. Måske hjælper det at træne modellen på en del svensk og norsk også, eller måske gør det ikke.

Der er altså mange forskningssprøgsmål som skal afklares i den kommende tid. Derfor er samarbejdejdet mellem Alexandra instituttet og universiteter afgørende for at lykkes med udvikling af danske sprogmodeller.

## De kommercielle modeller
Det er begrænsethvilken information de kommercielle virksomheder som Meta, OpenAI, Google, frigiver om hvilken data de bruger, og hvordan de brugen den. Meta har dog frigivet lidt information om deres nylige frigivet open source modeller Llama-3. Llama-3, som findes i en 8B- og 70B-parametermodeller, er trænet på "op til" 15 billioner tokens (https://ai.meta.com/blog/meta-llama-3/). Hvad dette fantisk betyder er uklart.

De fleste kommercielle spillere har en "multi-purpose-usage" tilgang til deres modeller, dvs., de udvikler sprogmodeller som f.eks. det at forstå mange sprog. Dette gør, sandsynligvis, at de konstakt vil forsøge at udvide størrelsen på de datasæt de træner modellerne på, løbende.

## Åben tilgang
Det er et stigende fokus fra open source communitiet i at skabe transparant omkring hvilken data sprogmodeller er trænet på, samt hvordan data kurakeres. Dette glæder også for Danish Foundation Model, hvor det er en fundamental præcis for alt vores arbejde.

HuggingFace b.la. for nyligt frigivet FineWeb (https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-v1), som er en large-scale sprogmodel præ-trænet på 15-billioner tokens, svarende til 44TB disk space. Det datasæt de har brugt er 96 snapshots af CommonCrawl (https://commoncrawl.org/). De har opnået ganske fine resultater.

For et lidt mere information omkring HugingFaces FineWeb tilgang, har Adam Hede (https://www.linkedin.com/in/adamhede/) skrevet en god blog post på LinkedIn om her https://www.linkedin.com/posts/adamhede_fineweb-decanting-the-web-for-the-finest-activity-7213413581910884352-CCya?utm_source=share&utm_medium=member_desktop.

## Use-cases og data
Munin sprogmodellerne vil være use-case drevet og fokuseret på det dansk sprog. Vi skal derfor, formodentlig, bruge mindre data for at kunne træne dansk sprogmodeller med fokus på specifikke use-cases. Vi vil løbende frigive information og vores datagrundlag, størrelse, etc.

## Mere research og vidensdeling
Det er altså ikke et simpelt sprøgsmål at svare på hvor meget og hvilken type data der skal til for at træne sprogmodeller. Vi vil løbende frigive mere information herom herom, når vi har lever flere research eksperimenter og er blever klogere på det.

Hvis du har nogen spørgsmål vedrørende DFM arbejde, er du altid velkommen til at kontakte os. Vi er meget åbne for dialog og sætter pris på input, da det hjælper os med at forbedre vores praksis og sikre, at vi er på den rette rejse. Din feedback er vigtig for os, og vi ser frem til at høre fra dig.
