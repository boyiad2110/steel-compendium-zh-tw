---
printing: "1.01"
printing_book: "Draw Steel: Monsters"
features:
    - cost: Encounter
      distance: Self
      effects:
        - effect: An enemy within 5 squares is reduced to 0 [Stamina](../../rule/health/stamina.md).
          name: Trigger
        - effect: The gnasher moves up to their speed and can use their [signature ability](../../rule/combat/signature-ability.md).
          name: Effect
      icon: ❗️
      level: 4
      name: Frenzied Bite
      sections:
        - label: Trigger
          text: An enemy within 5 squares is reduced to 0 [Stamina](../../rule/health/stamina.md).
        - label: Effect
          text: The gnasher moves up to their speed and can use their [signature ability](../../rule/combat/signature-ability.md).
      target: Self
      usage: Triggered action
    - cost: Encounter
      distance: Melee 1
      effects:
        - roll: Power Roll + highest characteristic
          tier1: 7 damage
          tier2: 11 damage
          tier3: 16 damage
      icon: "\U0001F5E1"
      keywords:
        - Melee
        - Strike
        - Weapon
      level: 7
      name: Flurry of Fangs
      power_roll:
        formula: + highest characteristic
        tiers:
            high: 16 damage
            low: 7 damage
            mid: 11 damage
      target: Three creatures or objects
      usage: Main action
    - cost: Encounter
      distance: Self
      effects:
        - effect: The gnasher reduces a creature to 0 [Stamina](../../rule/health/stamina.md).
          name: Trigger
        - effect: The gnasher consumes part of the target's body. The gnasher can spend a [Recovery](../../rule/health/recoveries.md), and each enemy within 5 squares of the gnasher who has I < AVERAGE is [frightened](../../condition/frightened.md) ([save](../../rule/general/saving-throw.md) ends).
          name: Effect
      icon: "\U0001F464"
      level: 10
      name: Horrific Feast
      sections:
        - label: Trigger
          text: The gnasher reduces a creature to 0 [Stamina](../../rule/health/stamina.md).
        - label: Effect
          text: The gnasher consumes part of the target's body. The gnasher can spend a [Recovery](../../rule/health/recoveries.md), and each enemy within 5 squares of the gnasher who has I < AVERAGE is [frightened](../../condition/frightened.md) ([save](../../rule/general/saving-throw.md) ends).
      target: Self
      usage: Main action
name: Gnoll Gnasher Advancement Features
scc: mcdm.monsters.v1/monster.retainer.advancement-features/gnoll-gnasher
type: featureblock
---

# Gnoll Gnasher Advancement Features

---

<div class="fb-wrap" data-role="feature">
<article class="fb md-typeset">
<header class="sc-head fb__head"><div class="sc-head__stack"><div class="sc-head__col sc-head__col--left"><div class="sc-head__slot sc-head__left-eyebrow sc-head__slot--line">Featureblock</div><h2 class="sc-head__slot sc-head__left-primary sc-head__slot--line">Gnoll Gnasher Advancement Features</h2></div></div><div class="sc-head__rail sc-head__col--right"></div></header>
<div class="fb__feats">
<div class="fb__band--adv" data-level="4">
<div class="fb__adv-head">Level 4 Advancement</div>
<article class="sc-ability fb__feat" data-action="triggered">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">❗️</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-frenzied-bite">Frenzied Bite</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Triggered action</div></div></header></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Self</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">Self</div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Trigger</span></div><div class="sc-ability__section-body"><p>An enemy within 5 squares is reduced to 0 <a href="../../../rule/health/stamina/">Stamina</a>.</p></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>The gnasher moves up to their speed and can use their <a href="../../../rule/combat/signature-ability/">signature ability</a>.</p></div></div>
</article>
</div>
<div class="fb__band--adv" data-level="7">
<div class="fb__adv-head">Level 7 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">🗡</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-flurry-of-fangs">Flurry of Fangs</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__kw"><span class="sc-ability__chip">Melee</span><span class="sc-ability__chip">Strike</span><span class="sc-ability__chip">Weapon</span></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Melee 1</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">Three creatures or objects</div></div></div>
<div class="sc-ability__pr"><div class="sc-ability__pr-head"><span class="sc-ability__dia"></span><span class="pre">Power Roll</span><span class="chars">+ highest characteristic</span></div><div class="sc-ability__pr-rows"><div class="sc-ability__tier" data-tier="low"><span class="badge">!</span><span class="res">7 damage</span></div><div class="sc-ability__tier" data-tier="mid"><span class="badge">@</span><span class="res">11 damage</span></div><div class="sc-ability__tier" data-tier="high"><span class="badge">#</span><span class="res">16 damage</span></div></div></div>
</article>
</div>
<div class="fb__band--adv" data-level="10">
<div class="fb__adv-head">Level 10 Advancement</div>
<article class="sc-ability fb__feat" data-action="main">
<div class="fb__feat-head"><header class="sc-head"><div class="sc-head__stack"><span class="fb__feat-icon">👤</span><div class="sc-head__col sc-head__col--left"><h3 class="sc-head__slot sc-head__left-primary sc-head__slot--line" id="sc-feat-horrific-feast">Horrific Feast</h3></div></div><div class="sc-head__rail sc-head__col--right"><div class="sc-head__slot sc-head__right-primary sc-head__slot--mini">Encounter</div><div class="sc-head__slot sc-head__right-deck sc-head__slot--chip">Main action</div></div></header></div>
<div class="sc-ability__rail"><div class="sc-ability__cell"><div class="l">Distance</div><div class="v">Self</div></div><div class="sc-ability__cell"><div class="l">Targets</div><div class="v">Self</div></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Trigger</span></div><div class="sc-ability__section-body"><p>The gnasher reduces a creature to 0 <a href="../../../rule/health/stamina/">Stamina</a>.</p></div></div>
<div class="sc-ability__section"><div class="sc-ability__section-head"><span class="sc-ability__dia"></span><span class="tag">Effect</span></div><div class="sc-ability__section-body"><p>The gnasher consumes part of the target&#39;s body. The gnasher can spend a <a href="../../../rule/health/recoveries/">Recovery</a>, and each enemy within 5 squares of the gnasher who has I &lt; AVERAGE is <a href="../../../condition/frightened/">frightened</a> (<a href="../../../rule/general/saving-throw/">save</a> ends).</p></div></div>
</article>
</div>
</div>
</article>
</div>


<template class="sc-src" data-fmt="md" data-src="&gt; **Level 4 Retainer Advancement Ability**&#10;&#10;&gt; ❗️ **Frenzied Bite (Encounter)**&#10;&gt;&#10;&gt; | **-**       | **&#91;Triggered action](../../rule/combat/triggered-action.md)** |&#10;&gt; |-------------|---------------------:|&#10;&gt; | **📏 Self** |          **🎯 Self** |&#10;&gt;&#10;&gt; **Trigger:** An enemy within 5 squares is reduced to 0 &#91;Stamina](../../rule/health/stamina.md).&#10;&gt;&#10;&gt; **Effect:** The gnasher moves up to their speed and can use their &#91;signature ability](../../rule/combat/signature-ability.md).&#10;&#10;&gt; **Level 7 Retainer Advancement Ability**&#10;&#10;&gt; 🗡 **Flurry of Fangs (Encounter)**&#10;&gt;&#10;&gt; | **Melee, Strike, Weapon** |                   **&#91;Main action](../../rule/combat/turn.md)** |&#10;&gt; |---------------------------|----------------------------------:|&#10;&gt; | **📏 Melee 1**            | **🎯 Three creatures or objects** |&#10;&gt;&#10;&gt; **Power Roll + highest characteristic:**&#10;&gt;&#10;&gt; - **≤11:** 7 damage&#10;&gt; - **12-16:** 11 damage&#10;&gt; - **17+:** 16 damage&#10;&#10;&gt; **Level 10 Retainer Advancement Ability**&#10;&#10;&gt; 👤 **Horrific Feast (Encounter)**&#10;&gt;&#10;&gt; | **-**       | **&#91;Main action](../../rule/combat/turn.md)** |&#10;&gt; |-------------|----------------:|&#10;&gt; | **📏 Self** |     **🎯 Self** |&#10;&gt;&#10;&gt; **Trigger:** The gnasher reduces a creature to 0 &#91;Stamina](../../rule/health/stamina.md).&#10;&gt;&#10;&gt; **Effect:** The gnasher consumes part of the target&#39;s body. The gnasher can spend a &#91;Recovery](../../rule/health/recoveries.md), and each enemy within 5 squares of the gnasher who has I &lt; AVERAGE is &#91;frightened](../../condition/frightened.md) (&#91;save](../../rule/general/saving-throw.md) ends)."></template>
