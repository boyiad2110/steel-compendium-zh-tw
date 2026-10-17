---
printing: "1.01"
printing_book: "Draw Steel: Monsters"
features:
    - cost: Encounter
      distance: Special; see below
      effects:
        - effect: The mortar fires a shell straight upward, which hovers 3 squares up in the air and sheds light below it in a 3 cube. Enemies illuminated by this light can't [hide](../../feature/common/maneuvers/hide.md) or turn invisible and can't benefit from concealment or cover. At the start of the mortar's next turn, the shell explodes to deal damage to enemies in the area.
          name: Effect
          roll: Power Roll + highest characteristic
          tier1: 5 fire damage
          tier2: 8 fire damage
          tier3: 11 fire damage
      icon: "\U0001F533"
      keywords:
        - Area
        - Ranged
        - Weapon
      level: 4
      name: Signal Shell
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 11 fire damage
            low: 5 fire damage
            mid: 8 fire damage
      sections:
        - label: Effect
          text: The mortar fires a shell straight upward, which hovers 3 squares up in the air and sheds light below it in a 3 cube. Enemies illuminated by this light can't [hide](../../feature/common/maneuvers/hide.md) or turn invisible and can't benefit from concealment or cover. At the start of the mortar's next turn, the shell explodes to deal damage to enemies in the area.
      target: Each enemy in the area
      usage: Main action
    - cost: Encounter
      distance: 10 x 1 line within 1
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 6 damage; P < WEAK [frightened](../../condition/frightened.md)
          tier2: 9 damage; P < AVERAGE [frightened](../../condition/frightened.md)
          tier3: 13 damage; P < STRONG [frightened](../../condition/frightened.md)
        - effect: Until the start of the mortar's next turn, [strikes](../../rule/combat/strike.md) made against the mortar or any ally [adjacent](../../rule/combat/adjacent.md) to them take a bane.
          name: Effect
      icon: "\U0001F533"
      keywords:
        - Area
        - Weapon
      level: 7
      name: Screaming Shell
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 13 damage; P < STRONG [frightened](../../condition/frightened.md)
            low: 6 damage; P < WEAK [frightened](../../condition/frightened.md)
            mid: 9 damage; P < AVERAGE [frightened](../../condition/frightened.md)
      sections:
        - label: Effect
          text: Until the start of the mortar's next turn, [strikes](../../rule/combat/strike.md) made against the mortar or any ally [adjacent](../../rule/combat/adjacent.md) to them take a bane.
      target: Each enemy in the area
      usage: Main action
    - cost: Encounter
      distance: 3 cube within 15
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 8 damage; I < WEAK [dazed](../../condition/dazed.md) ([save](../../rule/general/saving-throw.md) ends)
          tier2: 12 damage; I < AVERAGE [dazed](../../condition/dazed.md) ([save](../../rule/general/saving-throw.md) ends)
          tier3: 16 damage; I < STRONG [dazed](../../condition/dazed.md) ([save](../../rule/general/saving-throw.md) ends) and [prone](../../condition/prone.md)
      icon: "\U0001F533"
      keywords:
        - Area
        - Ranged
        - Weapon
      level: 10
      name: Pacifier Shell
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 16 damage; I < STRONG [dazed](../../condition/dazed.md) ([save](../../rule/general/saving-throw.md) ends) and [prone](../../condition/prone.md)
            low: 8 damage; I < WEAK [dazed](../../condition/dazed.md) ([save](../../rule/general/saving-throw.md) ends)
            mid: 12 damage; I < AVERAGE [dazed](../../condition/dazed.md) ([save](../../rule/general/saving-throw.md) ends)
      target: Each enemy in the area
      usage: Main action
name: Dwarf Mortar Advancement Features
scc: mcdm.monsters.v1/monster.retainer.advancement-features/dwarf-mortar
type: featureblock
---

# Dwarf Mortar Advancement Features

---

<div class="fb-wrap" data-role="feature">
<article class="fb md-typeset">
<header class="sc-head fb__head"><div class="sc-head__stack"><div class="sc-head__col sc-head__col--left"><div class="sc-head__slot sc-head__left-eyebrow sc-head__slot--line">Featureblock</div><h2 class="sc-head__slot sc-head__left-primary sc-head__slot--line">Dwarf Mortar Advancement Features</h2></div></div><div class="sc-head__rail sc-head__col--right"></div></header>
<div class="fb__feats">
<div class="fb__band--adv" data-level="4">
<div class="fb__adv-head">Level 4 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🔳</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-signal-shell">Signal Shell</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Area</span><span class="sc-ability__chip">Ranged</span><span class="sc-ability__chip">Weapon</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Special; see below</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">Each enemy in the area</div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>The mortar fires a shell straight upward, which hovers 3 squares up in the air and sheds light below it in a 3 cube. Enemies illuminated by this light can&#39;t <a href="../../../feature/common/maneuvers/hide/">hide</a> or turn invisible and can&#39;t benefit from concealment or cover. At the start of the mortar&#39;s next turn, the shell explodes to deal damage to enemies in the area.</p></div><div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">5 fire damage</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">8 fire damage</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">11 fire damage</span></div></div></div>
</div>
</article>
</div>
<div class="fb__band--adv" data-level="7">
<div class="fb__adv-head">Level 7 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🔳</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-screaming-shell">Screaming Shell</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Area</span><span class="sc-ability__chip">Weapon</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">10 x 1 line within 1</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">Each enemy in the area</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">6 damage; P &lt; WEAK <a href="../../../condition/frightened/">frightened</a></span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">9 damage; P &lt; AVERAGE <a href="../../../condition/frightened/">frightened</a></span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">13 damage; P &lt; STRONG <a href="../../../condition/frightened/">frightened</a></span></div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>Until the start of the mortar&#39;s next turn, <a href="../../../rule/combat/strike/">strikes</a> made against the mortar or any ally <a href="../../../rule/combat/adjacent/">adjacent</a> to them take a bane.</p></div></div>
</article>
</div>
<div class="fb__band--adv" data-level="10">
<div class="fb__adv-head">Level 10 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🔳</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-pacifier-shell">Pacifier Shell</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Area</span><span class="sc-ability__chip">Ranged</span><span class="sc-ability__chip">Weapon</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">3 cube within 15</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">Each enemy in the area</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">8 damage; I &lt; WEAK <a href="../../../condition/dazed/">dazed</a> (<a href="../../../rule/general/saving-throw/">save</a> ends)</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">12 damage; I &lt; AVERAGE <a href="../../../condition/dazed/">dazed</a> (<a href="../../../rule/general/saving-throw/">save</a> ends)</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">16 damage; I &lt; STRONG <a href="../../../condition/dazed/">dazed</a> (<a href="../../../rule/general/saving-throw/">save</a> ends) and <a href="../../../condition/prone/">prone</a></span></div></div></div>
</article>
</div>
</div>
</article>
</div>


<template class="sc-src" data-fmt="md" data-src="&gt; **Level 4 Retainer Advancement Ability**&#10;&#10;&gt; 🔳 **Signal Shell (Encounter)**&#10;&gt;&#10;&gt; | **Area, Ranged, Weapon**  |               **&#91;Main action](../../rule/combat/turn.md)** |&#10;&gt; |---------------------------|------------------------------:|&#10;&gt; | **📏 Special; see below** | **🎯 Each enemy in the area** |&#10;&gt;&#10;&gt; **Effect:** The mortar fires a shell straight upward, which hovers 3 squares up in the air and sheds light below it in a 3 cube. Enemies illuminated by this light can&#39;t &#91;hide](../../feature/common/maneuvers/hide.md) or turn invisible and can&#39;t benefit from concealment or cover. At the start of the mortar&#39;s next turn, the shell explodes to deal damage to enemies in the area.&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 5 fire damage&#10;&gt; - **12-16:** 8 fire damage&#10;&gt; - **17+:** 11 fire damage&#10;&#10;&gt; **Level 7 Retainer Advancement Ability**&#10;&#10;&gt; 🔳 **Screaming Shell (Encounter)**&#10;&gt;&#10;&gt; | **Area, Weapon**            |               **&#91;Main action](../../rule/combat/turn.md)** |&#10;&gt; |-----------------------------|------------------------------:|&#10;&gt; | **📏 10 x 1 line within 1** | **🎯 Each enemy in the area** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 6 damage; P &lt; WEAK &#91;frightened](../../condition/frightened.md)&#10;&gt; - **12-16:** 9 damage; P &lt; AVERAGE &#91;frightened](../../condition/frightened.md)&#10;&gt; - **17+:** 13 damage; P &lt; STRONG &#91;frightened](../../condition/frightened.md)&#10;&gt;&#10;&gt; **Effect:** Until the start of the mortar&#39;s next turn, &#91;strikes](../../rule/combat/strike.md) made against the mortar or any ally &#91;adjacent](../../rule/combat/adjacent.md) to them take a bane.&#10;&#10;&gt; **Level 10 Retainer Advancement Ability**&#10;&#10;&gt; 🔳 **Pacifier Shell (Encounter)**&#10;&gt;&#10;&gt; | **Area, Ranged, Weapon** |               **&#91;Main action](../../rule/combat/turn.md)** |&#10;&gt; |--------------------------|------------------------------:|&#10;&gt; | **📏 3 cube within 15**  | **🎯 Each enemy in the area** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 8 damage; I &lt; WEAK &#91;dazed](../../condition/dazed.md) (&#91;save](../../rule/general/saving-throw.md) ends)&#10;&gt; - **12-16:** 12 damage; I &lt; AVERAGE &#91;dazed](../../condition/dazed.md) (&#91;save](../../rule/general/saving-throw.md) ends)&#10;&gt; - **17+:** 16 damage; I &lt; STRONG &#91;dazed](../../condition/dazed.md) (&#91;save](../../rule/general/saving-throw.md) ends) and &#91;prone](../../condition/prone.md)"></template>
