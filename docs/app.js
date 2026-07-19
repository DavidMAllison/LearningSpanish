/* SI1M shared: identity + progress in localStorage, namespaced per user code. */

var SI1M = (function () {
  var GROUPS = [
    { n: 1, theme: "Foundation", days: [1, 2, 3, 4, 5] },
    { n: 2, theme: "Mortar", days: [6, 7, 8, 9, 10] },
    { n: 3, theme: "Bricks", days: [11, 12, 13, 14, 15] },
    { n: 4, theme: "Decoration", days: [16, 17, 18, 19, 20] }
  ];
  var SESSION_SIZE = 10;

  function param(name) {
    return new URLSearchParams(location.search).get(name);
  }

  // Identity: ?u=<code> wins and is remembered; otherwise last-used code.
  function currentCode() {
    var u = param("u");
    if (u) {
      localStorage.setItem("si1m_code", u.toLowerCase());
      return u.toLowerCase();
    }
    return localStorage.getItem("si1m_code");
  }

  function key(code) { return "si1m_user_" + code; }

  function load(code) {
    try {
      var raw = localStorage.getItem(key(code));
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return { name: "", group: 1, sessions: {}, quiz: {} };
  }

  function save(code, state) {
    localStorage.setItem(key(code), JSON.stringify(state));
  }

  function groupOf(day) {
    return GROUPS.find(function (g) { return g.days.indexOf(day) !== -1; });
  }

  function sessionsDone(state, day) {
    return (state.sessions[String(day)] || []).length;
  }

  function markSession(code, state, day, sessionIndex) {
    var k = String(day);
    var arr = state.sessions[k] || [];
    if (arr.indexOf(sessionIndex) === -1) arr.push(sessionIndex);
    state.sessions[k] = arr;
    save(code, state);
  }

  function recordQuiz(code, state, group, score, passScore) {
    var k = String(group);
    var q = state.quiz[k] || { attempts: 0, passed: false, best: 0 };
    q.attempts += 1;
    q.best = Math.max(q.best, score);
    if (score >= passScore) {
      q.passed = true;
      if (state.group === group) state.group = Math.min(group + 1, GROUPS.length + 1);
    }
    state.quiz[k] = q;
    save(code, state);
    return q;
  }

  // Keanu Koala — the family bot, here to cheer everyone on.
  var KEANU = {
    welcome: [
      "¡Hola, {name}! Keanu here. Ready for today's lesson? ¡Vamos!",
      "G'day {name}! This koala believes in you. Let's learn some Spanish!",
      "¡Hola, {name}! Eucalyptus for me, español for you. Let's climb!",
      "Welcome back, {name}! A little every day — that's the koala way."
    ],
    review: [
      "No worries, {name} — every great speaker stumbles. Let's review together and smash that quiz!",
      "You were SO close, {name}! One more look at the lessons and that quiz is yours.",
      "Koalas fall out of trees sometimes too, {name}. We climb back up. Let's review!"
    ],
    sessionDone: [
      "¡Muy bien, {name}! That's 10 more cards in your brain. Koala-ty work!",
      "Nice one, {name}! Small steps every day — that's how we climb the tree.",
      "¡Bien, {name}! Your brain just got a little more Spanish. I'm so proud!"
    ],
    dayDone: [
      "Day complete! ¡Fantástico, {name}! Go grab a snack — you earned it.",
      "You finished the whole day, {name}! This proud koala is doing a happy dance.",
      "¡Sí, {name}! Whole day done. High-five with my little koala paw. 🐾"
    ],
    quizPass: [
      "¡SÍ! You passed, {name}! I never doubted you for a second. New week unlocked!",
      "🎉 ¡Felicidades, {name}! You crushed it. On to the next adventure!",
      "That's my student! ¡Muy bien, {name}! The next week is all yours."
    ],
    quizFail: [
      "Hey {name} — not this time, and that's okay! Every miss teaches you something. Review with me and try again — you've got this.",
      "So close, {name}! Even koalas fall out of trees sometimes. Let's look at the lessons again and come back stronger.",
      "Almost, {name}! The quiz isn't going anywhere. A little review, a big comeback — I'll be right here."
    ],
    courseDone: [
      "¡Increíble, {name}! You finished the WHOLE course. This koala is speechless… almost. ¡Adiós y gracias!",
      "{name}, you did it ALL. Twenty days of Spanish! I'm the proudest koala in the eucalyptus tree."
    ]
  };

  function keanuMessage(context, name) {
    var pool = KEANU[context] || KEANU.welcome;
    var msg = pool[Math.floor(Math.random() * pool.length)];
    return msg.split("{name}").join(name || "amigo");
  }

  function keanuBubbleHTML(context, name) {
    return '<div class="keanu"><div class="avatar">🐨</div>' +
      '<div class="bubble"><div class="who">Keanu</div>' +
      keanuMessage(context, name) + "</div></div>";
  }

  return {
    GROUPS: GROUPS,
    SESSION_SIZE: SESSION_SIZE,
    param: param,
    currentCode: currentCode,
    load: load,
    save: save,
    groupOf: groupOf,
    sessionsDone: sessionsDone,
    markSession: markSession,
    recordQuiz: recordQuiz,
    keanuMessage: keanuMessage,
    keanuBubbleHTML: keanuBubbleHTML
  };
})();
