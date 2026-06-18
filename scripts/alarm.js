/* ============================================================
   scripts/alarm.js — 알림 설정 / D-Day 계산 / Firestore 저장
   사용: firebase-config.js, auth.js 로드 후 포함
   ============================================================ */

const MateAlarm = (() => {
  let _db = null;

  /* ── 초기화 ── */
  function init() {
    _db = firebase.firestore();
  }

  /* ── D-Day 계산 ── */
  function getDDayInfo(deadline) {
    if (!deadline) return null;

    const now  = new Date();
    now.setHours(0, 0, 0, 0);
    const due  = new Date(deadline);
    due.setHours(0, 0, 0, 0);
    const diff = Math.ceil((due - now) / (1000 * 60 * 60 * 24));

    if (diff < 0)  return { days: diff, label: '마감',    color: '#8896A6', bg: '#F2F5F9' };
    if (diff === 0) return { days: 0,   label: 'D-Day',   color: '#DC2626', bg: '#FEF2F2' };
    if (diff <= 7)  return { days: diff, label: `D-${diff}`, color: '#DC2626', bg: '#FEF2F2' };
    if (diff <= 29) return { days: diff, label: `D-${diff}`, color: '#B45309', bg: '#FEF3C7' };
    return             { days: diff, label: `D-${diff}`, color: '#00A868', bg: '#E6F7F1' };
  }

  /* ── 알림 설정 / 해제 ── */
  async function setAlarm(benefitId, benefitName, deadline, enabled) {
    const user = firebase.auth().currentUser;
    if (!user) throw new Error('로그인이 필요합니다');

    const docRef = _db.collection('user_alarms').doc(`${user.uid}_${benefitId}`);

    if (enabled) {
      await docRef.set({
        user_id:       user.uid,
        benefit_id:    benefitId,
        benefit_name:  benefitName,
        deadline:      deadline
          ? firebase.firestore.Timestamp.fromDate(new Date(deadline))
          : null,
        alarm_enabled: true,
        alarm_days:    [30, 14, 7, 3, 1],
        created_at:    firebase.firestore.FieldValue.serverTimestamp()
      });
    } else {
      await docRef.delete();
    }
  }

  /* ── 유저 알림 목록 조회 ── */
  async function getUserAlarms(userId) {
    const uid = userId || (firebase.auth().currentUser || {}).uid;
    if (!uid) return [];
    const snap = await _db.collection('user_alarms')
      .where('user_id', '==', uid)
      .where('alarm_enabled', '==', true)
      .get();
    return snap.docs.map(d => ({ id: d.id, ...d.data() }));
  }

  /* ── 특정 혜택 알림 설정 여부 확인 ── */
  async function isAlarmSet(benefitId) {
    const user = firebase.auth().currentUser;
    if (!user) return false;
    const doc = await _db.collection('user_alarms')
      .doc(`${user.uid}_${benefitId}`).get();
    return doc.exists && doc.data().alarm_enabled;
  }

  /* ── 알림 버튼 토글 UI 핸들러 ── */
  async function handleAlarmToggle(btn, benefitId, benefitName, deadline) {
    const user = firebase.auth().currentUser;
    if (!user) return false; // 비로그인 → 호출부에서 모달 처리

    btn.disabled = true;
    try {
      const currently = btn.dataset.alarmOn === 'true';
      const next      = !currently;
      await setAlarm(benefitId, benefitName, deadline, next);
      btn.dataset.alarmOn = next;
      btn.textContent = next ? '🔔 알림 ON' : '🔕 알림 OFF';
      btn.classList.toggle('alarm-on', next);
    } finally {
      btn.disabled = false;
    }
    return true;
  }

  return { init, getDDayInfo, setAlarm, getUserAlarms, isAlarmSet, handleAlarmToggle };
})();
