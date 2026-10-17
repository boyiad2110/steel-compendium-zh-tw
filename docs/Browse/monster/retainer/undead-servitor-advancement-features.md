---
printing: "1.01"
printing_book: "Draw Steel: Monsters"
features:
    - cost: Encounter
      distance: Melee 1
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 7 damage; M < WEAK [grabbed](../../condition/grabbed.md)
          tier2: 11 damage; M < AVERAGE [grabbed](../../condition/grabbed.md)
          tier3: 16 damage; M < STRONG [grabbed](../../condition/grabbed.md)
      icon: "\U0001F5E1"
      keywords:
        - Melee
        - Strike
        - Weapon
      level: 4
      name: Grab and Bite
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 16 damage; M < STRONG [grabbed](../../condition/grabbed.md)
            low: 7 damage; M < WEAK [grabbed](../../condition/grabbed.md)
            mid: 11 damage; M < AVERAGE [grabbed](../../condition/grabbed.md)
      target: One creature
      usage: Main action
    - cost: Encounter
      distance: Ranged 10
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 8 corruption damage; P < WEAK [weakened](../../condition/weakened.md) ([save](../../rule/general/saving-throw.md) ends)
          tier2: 13 corruption damage; P < AVERAGE [weakened](../../condition/weakened.md) ([save](../../rule/general/saving-throw.md) ends)
          tier3: 17 corruption damage; P < STRONG [weakened](../../condition/weakened.md) ([save](../../rule/general/saving-throw.md) ends)
        - effect: Before making the [strike](../../rule/combat/strike.md), the servitor can [teleport](../../movement/teleport.md) up to 10 squares to a space containing a dead creature, then burst out of the creature's body.
          name: Effect
      icon: "\U0001F3F9"
      keywords:
        - Magic
        - Ranged
        - Strike
      level: 7
      name: Death to Death
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 17 corruption damage; P < STRONG [weakened](../../condition/weakened.md) ([save](../../rule/general/saving-throw.md) ends)
            low: 8 corruption damage; P < WEAK [weakened](../../condition/weakened.md) ([save](../../rule/general/saving-throw.md) ends)
            mid: 13 corruption damage; P < AVERAGE [weakened](../../condition/weakened.md) ([save](../../rule/general/saving-throw.md) ends)
      sections:
        - label: Effect
          text: Before making the [strike](../../rule/combat/strike.md), the servitor can [teleport](../../movement/teleport.md) up to 10 squares to a space containing a dead creature, then burst out of the creature's body.
      target: One creature
      usage: Maneuver
    - cost: Encounter
      distance: 2 burst
      effects:
        - effect: The servitor is reduced to 0 [Stamina](../../rule/health/stamina.md).
          name: Trigger
        - effect: The servitor explodes.
          name: Effect
          roll: Power Roll + highest characteristic
          tier1: 6 corruption damage
          tier2: 10 corruption damage
          tier3: 14 corruption damage
      icon: ❗️
      keywords:
        - Area
        - Magic
      level: 10
      name: Death Miasma
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 14 corruption damage
            low: 6 corruption damage
            mid: 10 corruption damage
      sections:
        - label: Trigger
          text: The servitor is reduced to 0 [Stamina](../../rule/health/stamina.md).
        - label: Effect
          text: The servitor explodes.
      target: Each enemy in the area
      usage: Free triggered action
name: Undead Servitor Advancement Features
scc: mcdm.monsters.v1/monster.retainer.advancement-features/undead-servitor
type: featureblock
---

# Undead Servitor Advancement Features

---

<div class="fb-wrap" data-role="feature">
<article class="fb md-typeset">
<header class="sc-head fb__head"><div class="sc-head__stack"><div class="sc-head__col sc-head__col--left"><div class="sc-head__slot sc-head__left-eyebrow sc-head__slot--line">Featureblock</div><h2 class="sc-head__slot sc-head__left-primary sc-head__slot--line">Undead Servitor Advancement Features</h2></div></div><div class="sc-head__rail sc-head__col--right"></div></header>
<div class="fb__feats">
<div class="fb__band--adv" data-level="4">
<div class="fb__adv-head">Level 4 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🗡</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-grab-and-bite">Grab and Bite</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Melee</span><span class="sc-ability__chip">Strike</span><span class="sc-ability__chip">Weapon</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Melee 1</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">One creature</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">7 damage; M &lt; WEAK <a href="../../../condition/grabbed/">grabbed</a></span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">11 damage; M &lt; AVERAGE <a href="../../../condition/grabbed/">grabbed</a></span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">16 damage; M &lt; STRONG <a href="../../../condition/grabbed/">grabbed</a></span></div></div></div>
</article>
</div>
<div class="fb__band--adv" data-level="7">
<div class="fb__adv-head">Level 7 Advancement</div>
<article class="sc-ability fb__feat" data-action="maneuver">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🏹</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-death-to-death">Death to Death</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Maneuver</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Magic</span><span class="sc-ability__chip">Ranged</span><span class="sc-ability__chip">Strike</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Ranged 10</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">One creature</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">8 corruption damage; P &lt; WEAK <a href="../../../condition/weakened/">weakened</a> (<a href="../../../rule/general/saving-throw/">save</a> ends)</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">13 corruption damage; P &lt; AVERAGE <a href="../../../condition/weakened/">weakened</a> (<a href="../../../rule/general/saving-throw/">save</a> ends)</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">17 corruption damage; P &lt; STRONG <a href="../../../condition/weakened/">weakened</a> (<a href="../../../rule/general/saving-throw/">save</a> ends)</span></div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>Before making the <a href="../../../rule/combat/strike/">strike</a>, the servitor can <a href="../../../movement/teleport/">teleport</a> up to 10 squares to a space containing a dead creature, then burst out of the creature&#39;s body.</p></div></div>
</article>
</div>
<div class="fb__band--adv" data-level="10">
<div class="fb__adv-head">Level 10 Advancement</div>
<article class="sc-ability fb__feat" data-action="triggered">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">❗️</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-death-miasma">Death Miasma</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Free triggered action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Area</span><span class="sc-ability__chip">Magic</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">2 burst</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">Each enemy in the area</div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Trigger</span></div><div class="sc-ability__section-body"><p>The servitor is reduced to 0 <a href="../../../rule/health/stamina/">Stamina</a>.</p></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>The servitor explodes.</p></div><div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">6 corruption damage</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">10 corruption damage</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">14 corruption damage</span></div></div></div>
</div>
</article>
</div>
</div>
</article>
</div>


<template class="sc-src" data-fmt="md" data-src="&gt; **Level 4 Retainer Advancement Ability**&#10;&#10;&gt; 🗡 **Grab and Bite (Encounter)**&#10;&gt;&#10;&gt; | **Melee, Strike, Weapon** |     **&#91;Main action](../../rule/combat/turn.md)** |&#10;&gt; |---------------------------|--------------------:|&#10;&gt; | **📏 Melee 1**            | **🎯 One creature** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 7 damage; M &lt; WEAK &#91;grabbed](../../condition/grabbed.md)&#10;&gt; - **12-16:** 11 damage; M &lt; AVERAGE &#91;grabbed](../../condition/grabbed.md)&#10;&gt; - **17+:** 16 damage; M &lt; STRONG &#91;grabbed](../../condition/grabbed.md)&#10;&#10;&gt; **Level 7 Retainer Advancement Ability**&#10;&#10;&gt; 🏹 **Death to Death (Encounter)**&#10;&gt;&#10;&gt; | **Magic, Ranged, Strike** |        **&#91;Maneuver](../../rule/combat/turn.md)** |&#10;&gt; |---------------------------|--------------------:|&#10;&gt; | **📏 Ranged 10**          | **🎯 One creature** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 8 corruption damage; P &lt; WEAK &#91;weakened](../../condition/weakened.md) (&#91;save](../../rule/general/saving-throw.md) ends)&#10;&gt; - **12-16:** 13 corruption damage; P &lt; AVERAGE &#91;weakened](../../condition/weakened.md) (&#91;save](../../rule/general/saving-throw.md) ends)&#10;&gt; - **17+:** 17 corruption damage; P &lt; STRONG &#91;weakened](../../condition/weakened.md) (&#91;save](../../rule/general/saving-throw.md) ends)&#10;&gt;&#10;&gt; **Effect:** Before making the &#91;strike](../../rule/combat/strike.md), the servitor can &#91;teleport](../../movement/teleport.md) up to 10 squares to a space containing a dead creature, then burst out of the creature&#39;s body.&#10;&#10;&gt; **Level 10 Retainer Advancement Ability**&#10;&#10;&gt; ❗️ **Death Miasma (Encounter)**&#10;&gt;&#10;&gt; | **Area, Magic** |     **Free &#91;triggered action](../../rule/combat/triggered-action.md)** |&#10;&gt; |-----------------|------------------------------:|&#10;&gt; | **📏 2 burst**  | **🎯 Each enemy in the area** |&#10;&gt;&#10;&gt; **Trigger:** The servitor is reduced to 0 &#91;Stamina](../../rule/health/stamina.md).&#10;&gt;&#10;&gt; **Effect:** The servitor explodes.&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 6 corruption damage&#10;&gt; - **12-16:** 10 corruption damage&#10;&gt; - **17+:** 14 corruption damage"></template>
