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
    recordQuiz: recordQuiz
  };
})();
