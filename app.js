// Mage: The Ascension Character Generator — app.js (EN primary / ES secondary)
// Dependency-free, runs static on GitHub Pages.

const NATURES = ["Explorer","Protector","Rebel","Visionary","Caregiver","Leader","Outcast","Jester","Sage","Innocent","Hero","Martyr","Survivor","Revolutionary","Scholar","Thinker","Artisan","Strategist","Idealist","Mystic","Seeker","Guardian","Anarch"];
const DEMEANORS = ["Daring","Reserved","Charming","Stern","Introspective","Imposing","Mischievous","Sympathetic","Stoic","Charismatic","Cunning","Amiable","Discreet","Sardonic","Compassionate","Skeptical","Bold","Humorous","Inquisitive","Cautious","Noble","Arrogant","Witty","Solitary","Flamboyant","Pensive","Protective","Subdued","Confident","Dramatic","Pragmatic","Thoughtful","Idealistic","Tactful","Defiant","Empathetic","Resilient","Passionate","Assertive","Eccentric","Innovative","Traditional","Anarchic"];
const PARADIGMS = [
  "Hermetic high ritual and symbolic correspondence",
  "Super-science and advanced technology",
  "Shamanic pacts with the spirit world",
  "Divine authority and religious faith",
  "Artistic expression and sensory experience",
  "Chaotic chance and entropic decay",
  "Martial arts and control of internal energy (Chi/Ki)",
  "Hacking reality through a digital metaverse",
  "Primal connection to nature and the life force"
];
const MORALITY = ["Virtuous","Noble","Honorable","Just","Merciful","Neutral","Pragmatic","Calculating","Selfish","Cynical","Ruthless","Malevolent","Cruel","Monstrous"];
const SEXES = ["Male","Female","Non-binary","Agender","Genderfluid","Two-Spirit","Transgender","Intersex","Androgynous"];
const AGES = ["Young Adult (20-25)","Adult (26-35)","Middle-Aged (36-50)","Experienced (51-65)","Elderly (66-80)","Appears ageless due to magic","Looks younger than their actual age"];
const CONCEPTS = ["The Reluctant Hero","The Fallen Angel","The Seeker","The Scholar","The Chosen One","The Rebellious Outsider","The Tragic Hero","The Tormented Soul","The Visionary Leader","The Urban Shaman","The Corporate Warlock","The Reality Hacker","The Ascendant","The Eternal Nomad","The Digital Ghost","The Mad Genius"];
const BACKGROUNDS = ["A former soldier with a mysterious past.","An academic who delved too deep into forbidden knowledge.","A street-smart hustler with a knack for survival.","A gifted artist haunted by visions.","A gifted hacker who uncovers arcane truths hidden in the digital realm.","A wanderer who has traveled through various realms and dimensions.","A former member of a secret society, now seeking redemption.","A refugee from a war-torn land seeking a new life."];
const MERITS = ["Ambidextrous","Eidetic Memory","Natural Leader","Iron Will","Code of Honor","Sanctum (Level 3)","Unseen Sense","Danger Sense","Reputation","Arcane Heritage"];
const FLAWS = ["Addiction","Dark Secret","Enemy (Powerful)","Derangement","Overconfident","Vengeful","Amnesia","Notoriety","Haunted","Weak-Willed"];
const POSSESSIONS = ["An old, worn grimoire inherited from their mentor.","A pocket watch that runs backwards.","A cracked smartphone containing the ghost of a digital entity.","A shard of a mirror that shows glimpses of other worlds.","A silver ring that wards off bad luck."];
const SECRETS = ["Owes a life debt to a powerful and dangerous spirit.","Accidentally killed their mentor and covered it up.","Hides a Nephandic taint from their allies.","Possesses a forbidden grimoire that whispers to them.","Is a double agent for the Technocracy."];
const GOALS = ["Achieve personal Ascension.","Destroy a rival chantry or Technocracy construct.","Recover arcane knowledge to restore the value of magic.","Expose the Technocracy's control to the Sleeping masses.","Master a specific Sphere of magic to an unparalleled degree.","Create a new, safe haven for mages."];
const APPEARANCE = {
  skin: ["Very fair","Pale","Light olive","Medium tan","Warm beige","Golden brown","Caramel","Bronze","Rich mahogany","Deep espresso"],
  face: ["Oval","Round","Square","Heart-shaped","Diamond-shaped","Long","Triangular"],
  eyes: ["Blue","Green","Brown","Hazel","Gray","Violet","Silver"],
  hair_color: ["Black","Brown","Blonde","Red","Gray","White","Auburn","Platinum","Raven Black"],
  hair_style: ["Short and messy","Long and straight","Buzz cut","Dreadlocks","Elaborate braids","Slicked back","Bob cut","Mohawk","Bald"],
  build: ["Slender and willowy","Athletic and well-defined","Broad-shouldered and muscular","Stocky","Gaunt","Average"],
  height: ["Slightly below average","Of average height","Slightly taller than average","Imposingly tall"],
  clothing: ["Gothic and dark, with leather and lace","Bohemian and layered","Corporate and sharp, in well-tailored suits","Streetwear","Punk rock","Minimalist and functional","Academically rumpled","Vintage and anachronistic"]
};
const ATTRIBUTE_GROUPS = {
  Mental: ["Intelligence","Wits","Resolve"],
  Physical: ["Strength","Dexterity","Stamina"],
  Social: ["Presence","Manipulation","Composure"]
};
const ABILITY_GROUPS = {
  Talents: ["Alertness","Athletics","Brawl","Empathy","Expression","Intimidation","Persuasion","Streetwise","Subterfuge"],
  Skills: ["Animal Ken","Crafts","Drive","Etiquette","Firearms","Melee","Performance","Stealth","Survival"],
  Knowledges: ["Academics","Computer","Investigation","Law","Linguistics","Medicine","Occult","Politics","Science"]
};
const BACKGROUND_LIST = ["Resources","Allies","Contacts","Fame","Mentor","Retainer","Safehouse","Status"];
const HEALTH_LEVELS = ["Bruised (-0)","Hurt (-1)","Injured (-1)","Wounded (-2)","Mauled (-2)","Crippled (-5)","Incapacitated"];

function pick(arr){ return arr[Math.floor(Math.random()*arr.length)]; }
function pickObj(obj){ const keys=Object.keys(obj); return keys[Math.floor(Math.random()*keys.length)]; }

function randRange(min,max){ return Math.floor(Math.random()*(max-min+1))+min; }

function distributePoints(categories, pointsDist, maxPerItem, currentValues) {
  // categories: array of arrays of item names; pointsDist: points per category
  const values = {};
  for (const cat of categories) for (const item of cat) values[item] = (currentValues && currentValues[item]!==undefined) ? currentValues[item] : 0;
  for (let i=0;i<categories.length;i++){
    const cat = categories[i];
    let toSpend = pointsDist[i];
    while (toSpend > 0) {
      const item = pick(cat);
      if (values[item] < maxPerItem) { values[item]++; toSpend--; }
      // if all maxed, break
      if (cat.every(it => values[it] >= maxPerItem)) break;
    }
  }
  return values;
}

function generateCharacter(locks = {}) {
  // Affiliation
  const allAffiliations = {...MAGE_DATA.traditions, ...MAGE_DATA.conventions};
  const affKeys = Object.keys(allAffiliations);
  let affiliationKey = locks.affiliation ? locks.affiliation : pick(affKeys);
  let affiliationData = allAffiliations[affiliationKey];
  let factionType = MAGE_DATA.traditions[affiliationKey] ? "Tradition" : (MAGE_DATA.conventions[affiliationKey] ? "Convention" : "Craft/Other");

  const char = {
    name: locks.name || `${pick(["Alex","Jordan","Taylor","Morgan","Casey","Samantha","Derek","Robin","Jessie","Chris","Kendall","Quinn","Riley","Dakota","Hayden","Avery","Skylar","Emerson","Parker","Sage","Tatum","Reese"])} ${pick(["Smith","Johnson","Williams","Brown","Jones","Garcia","Morrison","Taylor","Murphy","Anderson","Parker","Harris","Martinez","Clark","Robinson","Young","Scott","Hill","Green","Adams","Baker","Nelson","Carter","Mitchell"])}`,
    nature: locks.nature || pick(NATURES),
    demeanor: locks.demeanor || pick(DEMEANORS),
    paradigm: locks.paradigm || pick(PARADIGMS),
    morality: locks.morality || pick(MORALITY),
    affiliation: affiliationKey,
    affiliationEn: affiliationData.en,
    affiliationEs: affiliationData.es,
    factionType,
    sphereAffinity: affiliationData.affinity,
    sex: pick(SEXES),
    age: pick(AGES),
    concept: locks.concept || pick(CONCEPTS),
    background: pick(BACKGROUNDS),
    merit: pick(MERITS),
    flaw: pick(FLAWS),
    possession: pick(POSSESSIONS),
    secret: pick(SECRETS),
    goal: pick(GOALS),
    story: "",
    // Appearance
    skin: pick(APPEARANCE.skin),
    face: pick(APPEARANCE.face),
    eyes: pick(APPEARANCE.eyes),
    hair_color: pick(APPEARANCE.hair_color),
    hair_style: pick(APPEARANCE.hair_style),
    build: pick(APPEARANCE.build),
    height: pick(APPEARANCE.height),
    clothing: pick(APPEARANCE.clothing),
    // Stats
    attributes: locks.attributes || distributePoints(Object.values(ATTRIBUTE_GROUPS), [7,5,3], 5, locks.attributes),
    abilities: locks.abilities || {
      Talents: distributePoints([ABILITY_GROUPS.Talents], [13], 3, locks.abilities && locks.abilities.Talents),
      Skills: distributePoints([ABILITY_GROUPS.Skills], [9], 3, locks.abilities && locks.abilities.Skills),
      Knowledges: distributePoints([ABILITY_GROUPS.Knowledges], [5], 3, locks.abilities && locks.abilities.Knowledges)
    },
    spheres: locks.spheres || {},
    backgrounds: locks.backgrounds || {},
    willpower: 5,
    paradox: 0,
    health: HEALTH_LEVELS.map(() => false)
  };

  // Spheres: affinity = 1, then 5 points, max 3 at creation
  MAGE_DATA.spheres.forEach(s => { char.spheres[s.en] = 0; });
  if (char.sphereAffinity && char.spheres[char.sphereAffinity] !== undefined) char.spheres[char.sphereAffinity] = 1;
  let points = 5;
  const sphereKeys = MAGE_DATA.spheres.map(s => s.en);
  while (points > 0) {
    const s = pick(sphereKeys);
    if (char.spheres[s] < 3) { char.spheres[s]++; points--; }
    if (sphereKeys.every(k => char.spheres[k] >= 3)) break;
  }
  // Backgrounds: 5 points
  BACKGROUND_LIST.forEach(b => { char.backgrounds[b] = 0; });
  points = 5;
  while (points > 0) {
    const b = pick(BACKGROUND_LIST);
    if (char.backgrounds[b] < 5) { char.backgrounds[b]++; points--; }
  }

  // Story template
  char.story = `${char.name} always seemed different. From a young age, they showed a remarkable aptitude that set them apart. Their awakening came in a moment of great tension, where their innate connection to magic manifested explosively, drawing the attention of the ${char.affiliation}. Their paradigm is ${char.paradigm.toLowerCase()}. Their greatest goal is ${char.goal.toLowerCase()} but this path is plagued by obstacles, including their flaw: ${char.flaw}. Their merit, ${char.merit}, is what allows them to press on. They always carry ${char.possession}`;

  return char;
}

window.MAGE_GEN = { generateCharacter, ATTRIBUTE_GROUPS, ABILITY_GROUPS, BACKGROUND_LIST, MAGE_DATA };

// ---------- UI ----------

const els = {
  affiliation: document.getElementById("affiliation"),
  nature: document.getElementById("nature"),
  demeanor: document.getElementById("demeanor"),
  paradigm: document.getElementById("paradigm"),
  morality: document.getElementById("morality"),
  sheet: document.getElementById("sheet"),
  page1: document.getElementById("page-1"),
  page2: document.getElementById("page-2")
};

function fillSelect(el, items, valueKey) {
  el.innerHTML = "";
  if (Array.isArray(items)) {
    items.forEach(it => { const o = document.createElement("option"); o.value = it; o.textContent = it; el.appendChild(o); });
  } else {
    Object.entries(items).forEach(([key, val]) => {
      const o = document.createElement("option"); o.value = key; o.textContent = val.en; el.appendChild(o);
    });
  }
}

function initDropdowns() {
  fillSelect(els.affiliation, {...MAGE_DATA.traditions, ...MAGE_DATA.conventions});
  fillSelect(els.nature, NATURES);
  fillSelect(els.demeanor, DEMEANORS);
  fillSelect(els.paradigm, PARADIGMS);
  fillSelect(els.morality, MORALITY);
}

function readLocks() {
  const lockConcept = document.getElementById("lock-concept").checked;
  return {
    affiliation: document.getElementById("affiliation").value,
    name: lockConcept ? (window.currentChar ? window.currentChar.name : null) : null,
    concept: lockConcept ? (window.currentChar ? window.currentChar.concept : null) : null,
    appearance: document.getElementById("lock-appearance").checked,
    attributes: document.getElementById("lock-attributes").checked ? window.currentChar.attributes : null,
    abilities: document.getElementById("lock-abilities").checked ? window.currentChar.abilities : null,
    spheres: document.getElementById("lock-spheres").checked ? window.currentChar.spheres : null,
    backgrounds: document.getElementById("lock-backgrounds").checked ? window.currentChar.backgrounds : null
  };
}

function dots(value, max = 5) {
  let html = "";
  for (let i = 1; i <= max; i++) html += `<span class="dot ${i <= value ? 'filled' : ''}">●</span>`;
  return html;
}

function renderSheet(char) {
  const p1 = els.page1;
  p1.innerHTML = `
    <div class="sheet-title">${char.name}</div>
    <div class="sheet-subtitle">${char.concept}</div>
    <div class="sheet-meta">
      <span class="chip"><strong>Nature:</strong> ${char.nature}</span>
      <span class="chip"><strong>Demeanor:</strong> ${char.demeanor}</span>
      <span class="chip"><strong>Affiliation:</strong> ${char.affiliationEn} <span class="es">(${char.affiliationEs})</span></span>
      <span class="chip"><strong>Faction:</strong> ${char.factionType}</span>
      <span class="chip"><strong>Sphere Affinity:</strong> ${char.sphereAffinity}</span>
    </div>

    <div class="section">
      <h3>Attributes / Atributos</h3>
      <div class="row">
        ${Object.entries(ATTRIBUTE_GROUPS).map(([group, attrs]) => `
          <div class="col">
            <div style="font-size:0.78rem; text-transform:uppercase; letter-spacing:1px; color:#5c4a3a; margin-bottom:4px;">${group}</div>
            ${attrs.map(a => `<div class="field"><strong>${a}:</strong> ${char.attributes[a]||0}</div>`).join("")}
          </div>
        `).join("")}
      </div>
    </div>

    <div class="section">
      <h3>Abilities / Habilidades</h3>
      <div class="row">
        ${Object.entries(char.abilities).map(([cat, items]) => `
          <div class="col">
            <div style="font-size:0.78rem; text-transform:uppercase; letter-spacing:1px; color:#5c4a3a; margin-bottom:4px;">${cat}</div>
            ${Object.entries(items).map(([abil, val]) => `<div class="field"><strong>${abil}:</strong> ${val}</div>`).join("")}
          </div>
        `).join("")}
      </div>
    </div>

    <div class="section">
      <h3>Spheres / Esferas</h3>
      <div class="row">
        ${MAGE_DATA.spheres.map(s => `
          <div class="col" style="flex:0 0 auto; min-width:110px;">
            <div class="field" style="font-size:0.82rem;"><strong>${s.en}</strong> <span class="es">(${s.es})</span></div>
            <div class="dots">${dots(char.spheres[s.en]||0, 5)}</div>
          </div>
        `).join("")}
      </div>
    </div>

    <div class="section">
      <h3>Backgrounds / Trasfondos</h3>
      <div class="row">
        ${Object.entries(char.backgrounds).map(([bg,val]) => `
          <div class="col" style="flex:0 0 auto; min-width:130px;">
            <div class="field">${bg}: ${dots(val,5)}</div>
          </div>
        `).join("")}
      </div>
    </div>

    <div class="section">
      <h3>Trackers / Rastreadores</h3>
      <div class="row">
        <div class="col" style="flex:1;">
          <div class="tracker">
            <div class="label">Willpower / Voluntad <span style="font-weight:normal">${char.willpower}/10</span></div>
            <div class="boxes">${Array(10).fill(0).map((_,i)=>`<div class="box ${i<char.willpower?'filled':''}"></div>`).join("")}</div>
          </div>
          <div class="tracker">
            <div class="label">Paradox / Paradoxa <span style="font-weight:normal">${char.paradox}</span></div>
            <div class="boxes">${Array(10).fill(0).map((_,i)=>`<div class="box ${i<char.paradox?'filled':''}"></div>`).join("")}</div>
          </div>
        </div>
        <div class="col" style="flex:1;">
          <div style="font-size:0.78rem; text-transform:uppercase; letter-spacing:1px; color:#5c4a3a; margin-bottom:4px;">Health / Salud</div>
          ${HEALTH_LEVELS.map((lvl,i)=>`<div class="tracker"><div class="label">${lvl}</div><div class="boxes"><div class="box ${char.health[i]?'filled':''}"></div></div></div>`).join("")}
        </div>
      </div>
    </div>

    <div class="section">
      <h3>Merits &amp; Flaws / Virtudes y Defectos</h3>
      <div class="mf"><div class="tag"><strong>Merit:</strong> ${char.merit}</div><div class="tag"><strong>Flaw:</strong> ${char.flaw}</div></div>
    </div>

    <div class="section">
      <h3>Appearance / Apariencia</h3>
      <div class="row">
        <div class="col">
          <div class="field"><strong>Sex:</strong> ${char.sex}</div>
          <div class="field"><strong>Age:</strong> ${char.age}</div>
          <div class="field"><strong>Build:</strong> ${char.build}</div>
          <div class="field"><strong>Height:</strong> ${char.height}</div>
        </div>
        <div class="col">
          <div class="field"><strong>Skin:</strong> ${char.skin}</div>
          <div class="field"><strong>Face:</strong> ${char.face}</div>
          <div class="field"><strong>Eyes:</strong> ${char.eyes}</div>
          <div class="field"><strong>Hair:</strong> ${char.hair_color} / ${char.hair_style}</div>
        </div>
        <div class="col">
          <div class="field"><strong>Clothing:</strong> ${char.clothing}</div>
        </div>
      </div>
    </div>

    <div class="section">
      <h3>Paradigm / Paradigma</h3>
      <div class="field">${char.paradigm}</div>
      <div class="field"><strong>Morality / Moralidad:</strong> ${char.morality}</div>
    </div>

    <div class="section">
      <h3>Possession / Posesión Apreciada</h3>
      <div class="field">${char.possession}</div>
    </div>

    <div class="section">
      <h3>Goal / Meta</h3>
      <div class="field">${char.goal}</div>
      <h3>Secret / Secreto</h3>
      <div class="field">${char.secret}</div>
      <h3>Background / Trasfondo</h3>
      <div class="field">${char.background}</div>
    </div>
  `;

  // Page 2: story
  const p2 = els.page2;
  p2.innerHTML = `
    <div class="sheet-title">${char.name} — Story &amp; Notes / Historia y Notas</div>
    <div class="story-box">
      <div style="font-size:0.78rem; text-transform:uppercase; letter-spacing:1px; color:#5c4a3a; margin-bottom:6px;">Character Story / Historia del Personaje</div>
      <div>${char.story}</div>
    </div>
  `;
  els.sheet.style.display = "block";
  window.currentChar = char;
}

let currentChar = null;
window.currentChar = null;

document.getElementById("btn-generate").addEventListener("click", () => {
  const locks = readLocks();
  const char = generateCharacter(locks);
  renderSheet(char);
});

document.getElementById("btn-random").addEventListener("click", () => {
  const char = generateCharacter();
  renderSheet(char);
});

document.getElementById("btn-print").addEventListener("click", () => {
  window.print();
});

document.getElementById("btn-pdf").addEventListener("click", () => {
  // PDF via browser print (Save as PDF). Trigger print dialog.
  window.print();
});

initDropdowns();

