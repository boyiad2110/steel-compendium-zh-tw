---
printing: "1.01"
printing_book: "Draw Steel: Monsters"
features:
    - cost: Encounter
      distance: Ranged 10
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 2 corruption damage; the target is cursed (EoT)
          tier2: 5 corruption damage; the target is cursed (EoT)
          tier3: 7 corruption damage; the target is cursed (EoT)
        - effect: While the target is cursed this way, whenever they make a strike that targets only one creature, the retainer can use a free triggered action to choose a second target for the strike within its distance.
          name: Effect
      icon: "\U0001F3F9"
      keywords:
        - Magic
        - Ranged
        - Strike
      level: 4
      name: Backfire Curse
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 7 corruption damage; the target is cursed (EoT)
            low: 2 corruption damage; the target is cursed (EoT)
            mid: 5 corruption damage; the target is cursed (EoT)
      sections:
        - label: Effect
          text: While the target is cursed this way, whenever they make a strike that targets only one creature, the retainer can use a free triggered action to choose a second target for the strike within its distance.
      target: One enemy
      usage: Main action
    - cost: Encounter
      distance: Ranged 10
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 5 damage; M < WEAK [slowed](../../../condition/slowed.md) ([save](../../../rule/general/saving-throw.md) ends)
          tier2: 9 damage; M < AVERAGE [slowed](../../../condition/slowed.md) ([save](../../../rule/general/saving-throw.md) ends)
          tier3: 12 damage; M < STRONG [slowed](../../../condition/slowed.md) ([save](../../../rule/general/saving-throw.md) ends)
        - effect: While the target is [slowed](../../../condition/slowed.md) this way, if they end their turn without moving on that turn, they are no longer [slowed](../../../condition/slowed.md) and are [restrained](../../../condition/restrained.md) ([save](../../../rule/general/saving-throw.md) ends).
          name: Effect
      icon: "\U0001F3F9"
      keywords:
        - Magic
        - Ranged
        - Strike
      level: 7
      name: Take Root
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 12 damage; M < STRONG [slowed](../../../condition/slowed.md) ([save](../../../rule/general/saving-throw.md) ends)
            low: 5 damage; M < WEAK [slowed](../../../condition/slowed.md) ([save](../../../rule/general/saving-throw.md) ends)
            mid: 9 damage; M < AVERAGE [slowed](../../../condition/slowed.md) ([save](../../../rule/general/saving-throw.md) ends)
      sections:
        - label: Effect
          text: While the target is [slowed](../../../condition/slowed.md) this way, if they end their turn without moving on that turn, they are no longer [slowed](../../../condition/slowed.md) and are [restrained](../../../condition/restrained.md) ([save](../../../rule/general/saving-throw.md) ends).
      target: One creature
      usage: Main action
    - cost: Encounter
      distance: Ranged 10
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 7 damage; if the target has M < WEAK they are mazed (save ends)
          tier2: 11 damage; if the target has M < AVERAGE they are mazed (save ends)
          tier3: 16 damage; if the target has M < STRONG they are mazed (save ends)
        - effect: While mazed, the target is [dazed](../../../condition/dazed.md). Additionally, at the end of each of the mazed target's turns, the retainer can cause the target to move up to their speed in a straight line in a direction of the retainer's choice. This is not [forced movement](../../../movement/forced-movement.md), and the movement ends if it would cause the target to enter [difficult](../../../movement/difficult-terrain.md) or damaging terrain.
          name: Effect
      icon: "\U0001F3F9"
      keywords:
        - Magic
        - Ranged
        - Strike
      level: 10
      name: Mazed
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 16 damage; if the target has M < STRONG they are mazed (save ends)
            low: 7 damage; if the target has M < WEAK they are mazed (save ends)
            mid: 11 damage; if the target has M < AVERAGE they are mazed (save ends)
      sections:
        - label: Effect
          text: While mazed, the target is [dazed](../../../condition/dazed.md). Additionally, at the end of each of the mazed target's turns, the retainer can cause the target to move up to their speed in a straight line in a direction of the retainer's choice. This is not [forced movement](../../../movement/forced-movement.md), and the movement ends if it would cause the target to enter [difficult](../../../movement/difficult-terrain.md) or damaging terrain.
      target: One creature
      usage: Main action
name: Hexer Abilities
scc: mcdm.monsters.v1/monster.retainer.role-advancement/hexer
type: featureblock
---

# Hexer Abilities

---

<div class="fb-wrap" data-role="feature">
<article class="fb md-typeset">
<header class="sc-head fb__head"><div class="sc-head__stack"><div class="sc-head__col sc-head__col--left"><div class="sc-head__slot sc-head__left-eyebrow sc-head__slot--line">Featureblock</div><h2 class="sc-head__slot sc-head__left-primary sc-head__slot--line">Hexer Abilities</h2></div></div><div class="sc-head__rail sc-head__col--right"></div></header>
<div class="fb__feats">
<div class="fb__band--adv" data-level="4">
<div class="fb__adv-head">Level 4 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🏹</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-backfire-curse">Backfire Curse</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Magic</span><span class="sc-ability__chip">Ranged</span><span class="sc-ability__chip">Strike</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Ranged 10</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">One enemy</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">2 corruption damage; the target is cursed (EoT)</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">5 corruption damage; the target is cursed (EoT)</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">7 corruption damage; the target is cursed (EoT)</span></div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>While the target is cursed this way, whenever they make a strike that targets only one creature, the retainer can use a free triggered action to choose a second target for the strike within its distance.</p></div></div>
</article>
</div>
<div class="fb__band--adv" data-level="7">
<div class="fb__adv-head">Level 7 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🏹</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-take-root">Take Root</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Magic</span><span class="sc-ability__chip">Ranged</span><span class="sc-ability__chip">Strike</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Ranged 10</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">One creature</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">5 damage; M &lt; WEAK <a href="../../../../condition/slowed/">slowed</a> (<a href="../../../../rule/general/saving-throw/">save</a> ends)</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">9 damage; M &lt; AVERAGE <a href="../../../../condition/slowed/">slowed</a> (<a href="../../../../rule/general/saving-throw/">save</a> ends)</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">12 damage; M &lt; STRONG <a href="../../../../condition/slowed/">slowed</a> (<a href="../../../../rule/general/saving-throw/">save</a> ends)</span></div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>While the target is <a href="../../../../condition/slowed/">slowed</a> this way, if they end their turn without moving on that turn, they are no longer <a href="../../../../condition/slowed/">slowed</a> and are <a href="../../../../condition/restrained/">restrained</a> (<a href="../../../../rule/general/saving-throw/">save</a> ends).</p></div></div>
</article>
</div>
<div class="fb__band--adv" data-level="10">
<div class="fb__adv-head">Level 10 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🏹</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-mazed">Mazed</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Magic</span><span class="sc-ability__chip">Ranged</span><span class="sc-ability__chip">Strike</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Ranged 10</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">One creature</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">7 damage; if the target has M &lt; WEAK they are mazed (save ends)</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">11 damage; if the target has M &lt; AVERAGE they are mazed (save ends)</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">16 damage; if the target has M &lt; STRONG they are mazed (save ends)</span></div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>While mazed, the target is <a href="../../../../condition/dazed/">dazed</a>. Additionally, at the end of each of the mazed target&#39;s turns, the retainer can cause the target to move up to their speed in a straight line in a direction of the retainer&#39;s choice. This is not <a href="../../../../movement/forced-movement/">forced movement</a>, and the movement ends if it would cause the target to enter <a href="../../../../movement/difficult-terrain/">difficult</a> or damaging terrain.</p></div></div>
</article>
</div>
</div>
</article>
</div>


<template class="sc-src" data-fmt="md" data-src="&gt; **Level 4 Role Advancement Ability**&#10;&#10;&gt; 🏹 **Backfire Curse (Encounter)**&#10;&gt;&#10;&gt; | **Magic, Ranged, Strike** |  **&#91;Main action](../../../rule/combat/turn.md)** |&#10;&gt; |---------------------------|-----------------:|&#10;&gt; | **📏 Ranged 10**          | **🎯 One enemy** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 2 corruption damage; the target is cursed (EoT)&#10;&gt; - **12-16:** 5 corruption damage; the target is cursed (EoT)&#10;&gt; - **17+:** 7 corruption damage; the target is cursed (EoT)&#10;&gt;&#10;&gt; **Effect:** While the target is cursed this way, whenever they make a strike that targets only one creature, the retainer can use a free triggered action to choose a second target for the strike within its distance.&#10;&#10;&gt; **Level 7 Role Advancement Ability**&#10;&#10;&gt; 🏹 **Take Root (Encounter)**&#10;&gt;&#10;&gt; | **Magic, Ranged, Strike** |     **&#91;Main action](../../../rule/combat/turn.md)** |&#10;&gt; |---------------------------|--------------------:|&#10;&gt; | **📏 Ranged 10**          | **🎯 One creature** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 5 damage; M &lt; WEAK &#91;slowed](../../../condition/slowed.md) (&#91;save](../../../rule/general/saving-throw.md) ends)&#10;&gt; - **12-16:** 9 damage; M &lt; AVERAGE &#91;slowed](../../../condition/slowed.md) (&#91;save](../../../rule/general/saving-throw.md) ends)&#10;&gt; - **17+:** 12 damage; M &lt; STRONG &#91;slowed](../../../condition/slowed.md) (&#91;save](../../../rule/general/saving-throw.md) ends)&#10;&gt;&#10;&gt; **Effect:** While the target is &#91;slowed](../../../condition/slowed.md) this way, if they end their turn without moving on that turn, they are no longer &#91;slowed](../../../condition/slowed.md) and are &#91;restrained](../../../condition/restrained.md) (&#91;save](../../../rule/general/saving-throw.md) ends).&#10;&#10;&gt; **Level 10 Role Advancement Ability**&#10;&#10;&gt; 🏹 **Mazed (Encounter)**&#10;&gt;&#10;&gt; | **Magic, Ranged, Strike** |     **&#91;Main action](../../../rule/combat/turn.md)** |&#10;&gt; |---------------------------|--------------------:|&#10;&gt; | **📏 Ranged 10**          | **🎯 One creature** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 7 damage; if the target has M &lt; WEAK they are mazed (save ends)&#10;&gt; - **12-16:** 11 damage; if the target has M &lt; AVERAGE they are mazed (save ends)&#10;&gt; - **17+:** 16 damage; if the target has M &lt; STRONG they are mazed (save ends)&#10;&gt;&#10;&gt; **Effect:** While mazed, the target is &#91;dazed](../../../condition/dazed.md). Additionally, at the end of each of the mazed target&#39;s turns, the retainer can cause the target to move up to their speed in a straight line in a direction of the retainer&#39;s choice. This is not &#91;forced movement](../../../movement/forced-movement.md), and the movement ends if it would cause the target to enter &#91;difficult](../../../movement/difficult-terrain.md) or damaging terrain."></template>
