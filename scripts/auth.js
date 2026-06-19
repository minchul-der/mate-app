/* ============================================================
   scripts/auth.js — Firebase Auth 래퍼
   사용: firebase-config.js 로드 후 이 파일을 포함
   ============================================================ */

const MateAuth = (() => {
  let _currentUser = null;
  const _listeners = [];

  function _auth() {
    return firebase.auth();
  }
  function _db() {
    return firebase.firestore();
  }

  /* ── 초기화 ── */
  function init() {
    _auth().onAuthStateChanged(user => {
      _currentUser = user;
      _listeners.forEach(fn => fn(user));
    });
  }

  /* ── 회원가입 ── */
  async function signUp(name, email, password, phone, onboardingData) {
    const cred = await _auth().createUserWithEmailAndPassword(email, password);
    await cred.user.updateProfile({ displayName: name });

    await _db().collection('users').doc(cred.user.uid).set({
      name,
      email,
      phone,
      onboarding: onboardingData || {},
      created_at: firebase.firestore.FieldValue.serverTimestamp()
    });

    return cred.user;
  }

  /* ── 로그인 ── */
  async function signIn(email, password) {
    const cred = await _auth().signInWithEmailAndPassword(email, password);
    return cred.user;
  }

  /* ── 로그아웃 ── */
  async function signOut() {
    await _auth().signOut();
  }

  /* ── 비밀번호 재설정 이메일 발송 ── */
  async function sendPasswordReset(email) {
    await _auth().sendPasswordResetEmail(email);
  }

  /* ── 이메일 재설정 (마이페이지용) ── */
  async function updatePassword(newPassword) {
    const user = _auth().currentUser;
    if (!user) throw new Error('로그인이 필요합니다');
    await user.updatePassword(newPassword);
  }

  /* ── 회원탈퇴 ── */
  async function deleteAccount() {
    const user = _auth().currentUser;
    if (!user) throw new Error('로그인이 필요합니다');
    await _db().collection('users').doc(user.uid).delete();
    const alarms = await _db().collection('user_alarms')
      .where('user_id', '==', user.uid).get();
    const batch = _db().batch();
    alarms.docs.forEach(d => batch.delete(d.ref));
    await batch.commit();
    await user.delete();
  }

  /* ── 유저 프로필 조회 ── */
  async function getUserProfile(uid) {
    const uid_ = uid || (_currentUser && _currentUser.uid);
    if (!uid_) return null;
    const doc = await _db().collection('users').doc(uid_).get();
    return doc.exists ? { id: doc.id, ...doc.data() } : null;
  }

  /* ── 온보딩 데이터 업데이트 ── */
  async function updateOnboarding(data) {
    const user = _auth().currentUser;
    if (!user) throw new Error('로그인이 필요합니다');
    await _db().collection('users').doc(user.uid).update({ onboarding: data });
  }

  /* ── 현재 유저 ── */
  function getCurrentUser() {
    return _currentUser;
  }

  /* ── 상태 변경 리스너 등록 ── */
  function onAuthStateChanged(fn) {
    _listeners.push(fn);
    if (typeof firebase !== 'undefined' && firebase.apps.length) {
      _auth().onAuthStateChanged(fn);
    }
  }

  return {
    init,
    signUp,
    signIn,
    signOut,
    sendPasswordReset,
    updatePassword,
    deleteAccount,
    getUserProfile,
    updateOnboarding,
    getCurrentUser,
    onAuthStateChanged,
  };
})();
