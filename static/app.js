document.addEventListener('DOMContentLoaded', () => {
    let currentMode = 'susi-ged';
    let inputMethod = 'quick';
    let currentResults = [];

    const defaultGPASubjects = [
        { name: '국어', credit: 4, val: 2.0 },
        { name: '수학', credit: 4, val: 2.5 },
        { name: '영어', credit: 4, val: 2.0 },
        { name: '한국사', credit: 2, val: 1.0 },
        { name: '사회/도덕', credit: 3, val: 2.0 },
        { name: '과학', credit: 3, val: 3.0 }
    ];

    const defaultGEDSubjects = [
        { name: '국어', score: 96 },
        { name: '수학', score: 92 },
        { name: '영어', score: 98 },
        { name: '한국사', score: 100 },
        { name: '사회', score: 95 },
        { name: '과학', score: 94 },
        { name: '선택과목(도덕/기술)', score: 98 }
    ];

    const defaultSATSubjects = [
        { name: '국어', raw: 88, percentile: 92, std: 132 },
        { name: '수학', raw: 84, percentile: 88, std: 128 },
        { name: '영어', raw: 92, percentile: '1등급', std: '-' },
        { name: '한국사', raw: 45, percentile: '1등급', std: '-' },
        { name: '탐구 1', raw: 42, percentile: 85, std: 62 },
        { name: '탐구 2', raw: 40, percentile: 80, std: 60 }
    ];

    let activeGPASubjects = JSON.parse(JSON.stringify(defaultGPASubjects));
    let activeGEDSubjects = JSON.parse(JSON.stringify(defaultGEDSubjects));
    let activeSATSubjects = JSON.parse(JSON.stringify(defaultSATSubjects));

    // Elements
    const modeTabs = document.querySelectorAll('.mode-tab');
    const btnToggleDetail = document.getElementById('btn-toggle-detail');
    const btnToggleQuick = document.getElementById('btn-toggle-quick');
    const sectionDetailInput = document.getElementById('section-detail-input');
    const sectionQuickInput = document.getElementById('section-quick-input');
    const detailGuideText = document.getElementById('detail-guide-text');
    
    const subjectTableHead = document.getElementById('subject-table-head');
    const subjectTableBody = document.getElementById('subject-table-body');
    const btnAddSubject = document.getElementById('btn-add-subject');
    const calcScoreInput = document.getElementById('calc-score-input');
    const calcAvgUnit = document.getElementById('calc-avg-unit');
    const summaryLabel = document.getElementById('summary-label');

    const scoreSlider = document.getElementById('score-slider');
    const scoreInput = document.getElementById('score-input');
    const scoreLabel = document.getElementById('score-label');
    const scoreUnit = document.getElementById('score-unit');
    const scoreHint = document.getElementById('score-hint');

    // 1. Sync Direct Input Box with Hidden state
    calcScoreInput.addEventListener('input', (e) => {
        const val = e.target.value;
        scoreInput.value = val;
        if (scoreSlider) scoreSlider.value = val;
    });

    scoreInput.addEventListener('input', (e) => {
        const val = e.target.value;
        calcScoreInput.value = val;
        if (scoreSlider) scoreSlider.value = val;
    });

    if (scoreSlider) {
        scoreSlider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value).toFixed(currentMode === 'susi-gpa' ? 2 : 1);
            scoreInput.value = val;
            calcScoreInput.value = val;
        });
    }

    calcScoreInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') runDiagnosis();
    });

    scoreInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') runDiagnosis();
    });
    
    const filterSort = document.getElementById('filter-sort');
    const filterRegion = document.getElementById('filter-region');
    const filterCategory = document.getElementById('filter-category');
    const filterType = document.getElementById('filter-type');
    const filterStatus = document.getElementById('filter-status');
    const groupCategory = document.getElementById('group-category');
    const groupType = document.getElementById('group-type');
    const btnSearch = document.getElementById('btn-search');
    const keywordSearch = document.getElementById('keyword-search');

    const statusBar = document.getElementById('status-bar');
    const resultsContainer = document.getElementById('results-container');
    const clickableChips = document.querySelectorAll('.clickable-chip');

    // 1. Fetch Summary Stats
    fetch('/api/summary')
        .then(res => res.json())
        .then(data => {
            document.getElementById('stat-susi').textContent = data.susi_units.toLocaleString();
            document.getElementById('stat-jungsi').textContent = data.jungsi_units.toLocaleString();
        })
        .catch(err => console.error(err));

    // 2. Input Method Toggle
    btnToggleDetail.addEventListener('click', () => {
        inputMethod = 'detail';
        btnToggleDetail.classList.add('active');
        btnToggleQuick.classList.remove('active');
        sectionDetailInput.style.display = 'block';
        sectionQuickInput.style.display = 'none';
    });

    btnToggleQuick.addEventListener('click', () => {
        inputMethod = 'quick';
        btnToggleQuick.classList.add('active');
        btnToggleDetail.classList.remove('active');
        sectionQuickInput.style.display = 'block';
        sectionDetailInput.style.display = 'none';
    });

    // 3. Mode Switcher (모바일 터치 및 PC 클릭 완벽 대응)
    modeTabs.forEach(tab => {
        let touchFired = false;
        const switchMode = (e) => {
            if (e.type === 'touchstart') {
                touchFired = true;
            } else if (e.type === 'click' && touchFired) {
                touchFired = false;
                return;
            }
            modeTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentMode = tab.dataset.mode;
            updateUIForMode(currentMode);
            runDiagnosis();
        };

        tab.addEventListener('click', switchMode);
        tab.addEventListener('touchstart', switchMode, { passive: true });
    });

    function updateUIForMode(mode) {
        const toggleContainer = document.getElementById('toggle-container');

        if (mode === 'susi-gpa') {
            if (toggleContainer) toggleContainer.style.display = 'flex';
            if (inputMethod === 'quick') {
                sectionQuickInput.style.display = 'block';
                sectionDetailInput.style.display = 'none';
            } else {
                sectionQuickInput.style.display = 'none';
                sectionDetailInput.style.display = 'block';
            }
            detailGuideText.textContent = '과목별 이수 단위수와 석차 등급을 입력하시면 단위수 가중평균 내신 등급이 자동 계산됩니다.';
            scoreLabel.textContent = '전과목 내신 평균 등급 (1.0 ~ 9.0 등급)';
            scoreUnit.textContent = '등급';
            scoreInput.min = '1.0'; scoreInput.max = '9.0'; scoreInput.value = '2.15';
            calcScoreInput.value = '2.15';
            scoreHint.textContent = '💡 1.0등급(최상위) ~ 9.0등급(최하위) | 원하시는 등급을 직접 입력하세요.';
            groupCategory.style.display = 'block';
            groupType.style.display = 'block';
            btnAddSubject.style.display = 'inline-block';
            filterType.innerHTML = `
                <option value="전체">전체 전형</option>
                <option value="학생부교과">학생부교과전형</option>
                <option value="학생부종합">학생부종합전형</option>
                <option value="논술">논술전형</option>
            `;
        } else if (mode === 'susi-ged') {
            if (toggleContainer) toggleContainer.style.display = 'flex';
            if (inputMethod === 'quick') {
                sectionQuickInput.style.display = 'block';
                sectionDetailInput.style.display = 'none';
            } else {
                sectionQuickInput.style.display = 'none';
                sectionDetailInput.style.display = 'block';
            }
            detailGuideText.textContent = '검정고시 과목별 원점수(0~100점)만 입력하시면 전과목 원점수 평균 및 대학별 환산 등급이 자동 계산됩니다.';
            scoreLabel.textContent = '검정고시 전과목 평균 점수 (0 ~ 100점)';
            scoreUnit.textContent = '점';
            scoreInput.min = '0'; scoreInput.max = '100'; scoreInput.value = '96.1';
            calcScoreInput.value = '96.1';
            scoreHint.textContent = '💡 원하시는 검정고시 평균 점수를 숫자란에 직접 입력(예: 96.1, 98.5 등)하세요. (학종/지원불가전형 자동제외)';
            groupCategory.style.display = 'block';
            groupType.style.display = 'block';
            btnAddSubject.style.display = 'inline-block';
            filterType.innerHTML = `
                <option value="전체">전체 가능전형 (교과/논술)</option>
                <option value="학생부교과">학생부교과전형 (인정 대학만)</option>
                <option value="논술">논술전형 (비교내신 적용)</option>
            `;
            if (filterType.value === '학생부종합') filterType.value = '전체';
        } else if (mode === 'jungsi-sat') {
            // 정시 모드: 평균 백분위 박스를 완전히 숨기고, 과목별 점수 입력창만 전면 배치
            if (toggleContainer) toggleContainer.style.display = 'none';
            sectionQuickInput.style.display = 'none';
            sectionDetailInput.style.display = 'block';
            detailGuideText.textContent = '수능 과목별 원점수 및 백분위(국/수/영/탐1/탐2)를 입력하시면 3개년 백분위 컷 기반으로 정시 지원이 자동 진단됩니다.';
            scoreLabel.textContent = '수능 국/수/탐 평균 백분위 (0 ~ 100점)';
            scoreUnit.textContent = '점';
            scoreInput.min = '0'; scoreInput.max = '100'; scoreInput.value = '85.0';
            calcScoreInput.value = '85.0';
            scoreHint.textContent = '💡 2023~2025 정시 합격자 70% Cutoff 백분위 데이터를 기반으로 정시를 진단합니다.';
            groupCategory.style.display = 'none';
            groupType.style.display = 'none';
            btnAddSubject.style.display = 'none';
        }

        renderSubjectTable();
    }

    function recalcGPA() {
        let totalCredit = 0;
        let weightedSum = 0;
        activeGPASubjects.forEach(subj => {
            totalCredit += parseFloat(subj.credit) || 0;
            weightedSum += (parseFloat(subj.credit) || 0) * (parseFloat(subj.val) || 0);
        });
        const avg = totalCredit > 0 ? (weightedSum / totalCredit) : 2.5;
        const avgVal = avg.toFixed(2);
        calcScoreInput.value = avgVal;
        scoreInput.value = avgVal;
        if (scoreSlider) scoreSlider.value = avgVal;
    }

    function recalcGED() {
        let totalScore = 0;
        activeGEDSubjects.forEach(subj => {
            totalScore += parseFloat(subj.score) || 0;
        });
        const avg = activeGEDSubjects.length > 0 ? (totalScore / activeGEDSubjects.length) : 95.0;
        const avgVal = avg.toFixed(1);
        calcScoreInput.value = avgVal;
        scoreInput.value = avgVal;
        if (scoreSlider) scoreSlider.value = avgVal;
    }

    function recalcSAT() {
        let sumPercentile = 0;
        let countP = 0;
        activeSATSubjects.forEach(subj => {
            const isGradeSubject = subj.name.includes('영어') || subj.name.includes('한국사');
            if (!isGradeSubject && typeof subj.percentile === 'number') {
                sumPercentile += subj.percentile;
                countP++;
            }
        });
        const avgP = countP > 0 ? (sumPercentile / countP) : 85.0;
        const avgVal = avgP.toFixed(1);
        calcScoreInput.value = avgVal;
        scoreInput.value = avgVal;
        if (scoreSlider) scoreSlider.value = avgVal;
    }

    function renderSubjectTable() {
        subjectTableBody.innerHTML = '';

        if (currentMode === 'susi-gpa') {
            summaryLabel.textContent = '계산된 내신 등급:';
            subjectTableHead.innerHTML = `
                <tr>
                    <th>교과목명</th>
                    <th>이수 단위수</th>
                    <th>석차 등급 (1~9)</th>
                    <th>단위수 x 등급</th>
                    <th>삭제</th>
                </tr>
            `;

            activeGPASubjects.forEach((subj, idx) => {
                const tr = document.createElement('tr');
                const subScore = (subj.credit * subj.val).toFixed(1);

                tr.innerHTML = `
                    <td><input type="text" value="${subj.name}" class="inp-gpa-name" data-idx="${idx}"></td>
                    <td><input type="number" min="1" max="10" value="${subj.credit}" class="inp-gpa-credit" data-idx="${idx}"></td>
                    <td><input type="number" step="0.1" min="1.0" max="9.0" value="${subj.val}" class="inp-gpa-val" data-idx="${idx}"></td>
                    <td style="font-weight:700; color:#a5b4fc;" class="cell-subscore-${idx}">${subScore}</td>
                    <td><button type="button" class="btn-del-subj" data-type="gpa" data-idx="${idx}" style="background:transparent; border:none; color:#ef4444; cursor:pointer;"><i class="fa-solid fa-trash-can"></i></button></td>
                `;
                subjectTableBody.appendChild(tr);
            });

            calcAvgUnit.textContent = '등급';
            recalcGPA();

            document.querySelectorAll('.inp-gpa-name').forEach(inp => inp.addEventListener('input', e => activeGPASubjects[e.target.dataset.idx].name = e.target.value));
            document.querySelectorAll('.inp-gpa-credit').forEach(inp => inp.addEventListener('input', e => { 
                const idx = e.target.dataset.idx;
                activeGPASubjects[idx].credit = parseFloat(e.target.value)||0; 
                const cell = document.querySelector(`.cell-subscore-${idx}`);
                if (cell) cell.textContent = (activeGPASubjects[idx].credit * activeGPASubjects[idx].val).toFixed(1);
                recalcGPA(); 
            }));
            document.querySelectorAll('.inp-gpa-val').forEach(inp => inp.addEventListener('input', e => { 
                const idx = e.target.dataset.idx;
                activeGPASubjects[idx].val = parseFloat(e.target.value)||0; 
                const cell = document.querySelector(`.cell-subscore-${idx}`);
                if (cell) cell.textContent = (activeGPASubjects[idx].credit * activeGPASubjects[idx].val).toFixed(1);
                recalcGPA(); 
            }));

        } else if (currentMode === 'susi-ged') {
            summaryLabel.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> 검정고시 계산된 평균:';
            subjectTableHead.innerHTML = `
                <tr>
                    <th>검정고시 과목명</th>
                    <th>원점수 (0~100점)</th>
                    <th>상태</th>
                    <th>삭제</th>
                </tr>
            `;

            activeGEDSubjects.forEach((subj, idx) => {
                const tr = document.createElement('tr');
                const score = parseFloat(subj.score) || 0;
                const statusTag = score >= 95 ? '<span style="color:#10b981; font-weight:700;">우수</span>' : score >= 80 ? '<span style="color:#3b82f6; font-weight:700;">보통</span>' : '<span style="color:#f59e0b;">미흡</span>';

                tr.innerHTML = `
                    <td><input type="text" value="${subj.name}" class="inp-ged-name" data-idx="${idx}"></td>
                    <td><input type="number" min="0" max="100" value="${subj.score}" class="inp-ged-score" data-idx="${idx}"></td>
                    <td>${statusTag}</td>
                    <td><button type="button" class="btn-del-subj" data-type="ged" data-idx="${idx}" style="background:transparent; border:none; color:#ef4444; cursor:pointer;"><i class="fa-solid fa-trash-can"></i></button></td>
                `;
                subjectTableBody.appendChild(tr);
            });

            calcAvgUnit.textContent = '점';
            recalcGED();

            document.querySelectorAll('.inp-ged-name').forEach(inp => inp.addEventListener('input', e => activeGEDSubjects[e.target.dataset.idx].name = e.target.value));
            document.querySelectorAll('.inp-ged-score').forEach(inp => inp.addEventListener('input', e => { 
                const idx = e.target.dataset.idx;
                activeGEDSubjects[idx].score = parseFloat(e.target.value)||0; 
                recalcGED(); 
            }));

        } else if (currentMode === 'jungsi-sat') {
            summaryLabel.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> 수능 계산된 평균 백분위:';
            subjectTableHead.innerHTML = `
                <tr>
                    <th>수능 영역</th>
                    <th>원점수 (0~100)</th>
                    <th>백분위 (0~100)</th>
                    <th>표준점수</th>
                </tr>
            `;

            activeSATSubjects.forEach((subj, idx) => {
                const tr = document.createElement('tr');
                const isGradeSubject = subj.name.includes('영어') || subj.name.includes('한국사');

                tr.innerHTML = `
                    <td style="font-weight:700; color:#e2e8f0;">${subj.name}</td>
                    <td><input type="number" min="0" max="100" value="${subj.raw}" class="inp-sat-raw" data-idx="${idx}"></td>
                    <td><input type="${isGradeSubject ? 'text' : 'number'}" value="${subj.percentile}" class="inp-sat-p" data-idx="${idx}"></td>
                    <td><input type="text" value="${subj.std}" class="inp-sat-std" data-idx="${idx}"></td>
                `;
                subjectTableBody.appendChild(tr);
            });

            calcAvgUnit.textContent = '점';
            recalcSAT();

            document.querySelectorAll('.inp-sat-raw').forEach(inp => inp.addEventListener('input', e => activeSATSubjects[e.target.dataset.idx].raw = parseFloat(e.target.value)||0));
            document.querySelectorAll('.inp-sat-p').forEach(inp => inp.addEventListener('input', e => {
                const idx = e.target.dataset.idx;
                const isGradeSubject = activeSATSubjects[idx].name.includes('영어') || activeSATSubjects[idx].name.includes('한국사');
                activeSATSubjects[idx].percentile = isGradeSubject ? e.target.value : (parseFloat(e.target.value)||0);
                recalcSAT();
            }));
            document.querySelectorAll('.inp-sat-std').forEach(inp => inp.addEventListener('input', e => activeSATSubjects[e.target.dataset.idx].std = e.target.value));
        }

        document.querySelectorAll('.btn-del-subj').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const type = btn.dataset.type;
                const idx = btn.dataset.idx;
                if (type === 'gpa') activeGPASubjects.splice(idx, 1);
                if (type === 'ged') activeGEDSubjects.splice(idx, 1);
                renderSubjectTable();
            });
        });
    }

    btnAddSubject.addEventListener('click', () => {
        if (currentMode === 'susi-gpa') {
            activeGPASubjects.push({ name: `선택과목 ${activeGPASubjects.length + 1}`, credit: 2, val: 2.5 });
        } else if (currentMode === 'susi-ged') {
            activeGEDSubjects.push({ name: `선택과목 ${activeGEDSubjects.length + 1}`, score: 95 });
        }
        renderSubjectTable();
    });

    renderSubjectTable();

    // 5. Search Trigger (하바나-트리니티 엔진 가동 버튼 클릭 시 동작)
    if (btnSearch) {
        btnSearch.addEventListener('click', (e) => {
            e.preventDefault();
            btnSearch.style.transform = 'scale(0.96)';
            setTimeout(() => { btnSearch.style.transform = 'none'; }, 150);
            runDiagnosis(true);
        });
    }

    function runDiagnosis(isManualClick = false) {
        let val = parseFloat(calcScoreInput ? calcScoreInput.value : '');
        if (isNaN(val)) val = parseFloat(scoreInput ? scoreInput.value : '');
        if (isNaN(val)) {
            if (currentMode === 'susi-gpa') val = 2.15;
            else if (currentMode === 'susi-ged') val = 96.1;
            else val = 85.0;
        }

        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <p>하바나-트리니티 대입 엔진 가동 중입니다 (전국 모집단위 종합 산출 중)...</p>
            </div>
        `;

        if (isManualClick) {
            const statusBar = document.getElementById('status-bar');
            if (statusBar) {
                statusBar.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        const filterUnivType = document.getElementById('filter-univ-type');
        const univTypeVal = filterUnivType ? filterUnivType.value : '전체';
        const filterDeptSelect = document.getElementById('filter-dept');
        const selectedDept = filterDeptSelect ? filterDeptSelect.value : '';

        if (currentMode === 'susi-gpa' || currentMode === 'susi-ged') {
            const inputType = currentMode === 'susi-gpa' ? 'gpa' : 'ged';
            const url = `/api/analyze/susi?input_type=${inputType}&score=${val}&region=${encodeURIComponent(filterRegion.value)}&category=${encodeURIComponent(filterCategory.value)}&admission_type=${encodeURIComponent(filterType.value)}&univ_type=${encodeURIComponent(univTypeVal)}&dept=${encodeURIComponent(selectedDept)}&limit=1500`;
            
            fetch(url)
                .then(res => res.json())
                .then(data => {
                    currentResults = data.results || [];
                    updateDepartmentDropdown();
                    renderResults();
                });
        } else {
            const url = `/api/analyze/jungsi?percentile=${val}&region=${encodeURIComponent(filterRegion.value)}&dept=${encodeURIComponent(selectedDept)}&limit=1500`;
            
            fetch(url)
                .then(res => res.json())
                .then(data => {
                    currentResults = data.results || [];
                    updateDepartmentDropdown();
                    renderResults();
                });
        }
    }

    let currentStatusFilter = '전체';

    function updateDepartmentDropdown() {
        const filterDeptSelect = document.getElementById('filter-dept');
        if (!filterDeptSelect) return;

        const depts = Array.from(new Set(currentResults.map(r => r.department).filter(Boolean)));
        depts.sort((a, b) => a.localeCompare(b, 'ko'));

        const currentVal = filterDeptSelect.value;
        filterDeptSelect.innerHTML = `<option value="">🔍 전체/희망 학과 선택 (${depts.length}개 학과 - 가나다순)</option>` +
            depts.map(d => `<option value="${d}">${d}</option>`).join('');
        
        if (depts.includes(currentVal)) {
            filterDeptSelect.value = currentVal;
        }
    }

    // Clickable Chip Listeners for Filtering/Sorting by Status Code
    clickableChips.forEach(chip => {
        chip.addEventListener('click', () => {
            currentStatusFilter = chip.dataset.status || '전체';
            renderResults();
        });
    });

    const filterDeptSelect = document.getElementById('filter-dept');
    if (filterDeptSelect) {
        filterDeptSelect.addEventListener('change', () => {
            runDiagnosis();
        });
    }

    const filterUnivTypeSelect = document.getElementById('filter-univ-type');
    if (filterUnivTypeSelect) {
        filterUnivTypeSelect.addEventListener('change', runDiagnosis);
    }

    filterRegion.addEventListener('change', runDiagnosis);
    filterCategory.addEventListener('change', runDiagnosis);
    filterType.addEventListener('change', runDiagnosis);
    keywordSearch.addEventListener('input', () => {
        renderResults();
    });

    // 6. Render Results
    function renderResults() {
        const filterDeptSelect = document.getElementById('filter-dept');
        const selectedDept = filterDeptSelect ? filterDeptSelect.value : '';
        const kw = keywordSearch.value.trim().toLowerCase();

        // Highlight Active Chip
        clickableChips.forEach(chip => {
            if (chip.dataset.status === currentStatusFilter) {
                chip.classList.add('active');
            } else {
                chip.classList.remove('active');
            }
        });

        // Compute base filtered results (department & keyword filtering applied first)
        let baseFiltered = currentResults.filter(item => {
            if (selectedDept && item.department !== selectedDept) return false;
            if (kw.length > 0) {
                const text = `${item.univ} ${item.department} ${item.type || ''} ${item.sub_type || ''}`.toLowerCase();
                if (!text.includes(kw)) return false;
            }
            return true;
        });

        // Compute dynamic counts across baseFiltered items
        const sosoCount = baseFiltered.filter(i => i.status.includes('소신')).length;
        const fitCount = baseFiltered.filter(i => i.status.includes('적정')).length;
        const safeCount = baseFiltered.filter(i => i.status.includes('안정')).length;

        document.getElementById('count-soso').textContent = sosoCount.toLocaleString();
        document.getElementById('count-fit').textContent = fitCount.toLocaleString();
        document.getElementById('count-safe').textContent = safeCount.toLocaleString();
        document.getElementById('count-all').textContent = baseFiltered.length.toLocaleString();

        let filtered = baseFiltered.filter(item => {
            if (currentStatusFilter !== '전체' && !item.status.includes(currentStatusFilter)) return false;
            return true;
        });

        statusBar.style.display = 'flex';

        if (filtered.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    <p>선택하신 조건(범주 [${currentStatusFilter}], 학과 [${selectedDept || '전체'}])에 해당하거나 검색 조건에 일치하는 모집단위가 없습니다.</p>
                </div>
            `;
            return;
        }

        // Render top 150 cards for lightning fast performance while keeping exact totals
        const displayList = filtered.slice(0, 150);

        let html = '';

        if (filtered.length > 150) {
            html += `
                <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3); color: #c7d2fe; padding: 12px 20px; border-radius: 14px; font-size: 13.5px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
                    <span><i class="fa-solid fa-circle-info"></i> 총 <strong>${filtered.length.toLocaleString()}</strong>개 모집단위 중 <strong>소신 우선 (상위 150개)</strong> 표시 중</span>
                    <span style="font-size: 12px; color: #a5b4fc;">* 상단 [소신/적정/안정] 뱃지 또는 학과 목록 필터를 이용하시면 원하시는 항목을 더 빠르게 보실 수 있습니다.</span>
                </div>
            `;
        }

        html += '<div class="results-grid">';
        displayList.forEach(item => {
            let badgeClass = 'badge-safe';
            if (item.status.includes('적정')) badgeClass = 'badge-fit';
            if (item.status.includes('소신')) badgeClass = 'badge-soso';

            const tierBadge = item.tier <= 5 ? `<span class="rank-pill">Tier ${item.tier} 주요대</span>` : '';

            if (currentMode === 'susi-gpa' || currentMode === 'susi-ged') {
                const convertedText = currentMode === 'susi-ged' ? `
                    <div class="ged-converted-highlight" style="background: rgba(139, 92, 246, 0.15); border: 1px dashed rgba(139, 92, 246, 0.4); padding: 8px 12px; border-radius: 8px; margin: 8px 0 10px 0; color: #c4b5fd; font-size: 13px;">
                        <i class="fa-solid fa-calculator"></i> 대학별 검정고시 환산등급: <strong style="color: #a78bfa; font-size: 14px;">${item.user_grade}</strong>
                    </div>` : '';
                html += `
                    <div class="res-card">
                        <div class="res-header">
                            <div>
                                <div class="res-univ">${item.univ} ${tierBadge}</div>
                                <div class="res-region"><i class="fa-solid fa-location-dot"></i> ${item.region} | ${item.type} (${item.sub_type})</div>
                            </div>
                            <span class="status-badge ${badgeClass}">${item.status.split(' ')[0]}</span>
                        </div>
                        <div class="res-dept">${item.department}</div>
                        <div class="res-details">
                            <div class="cutoff-3yr-box">
                                <span>3개년 평균 컷: <strong>${item.cutoff_3yr} 등급</strong></span>
                                <div class="cutoff-years">
                                    <span class="year-tag">'25: ${item.cut_2025}</span>
                                    <span class="year-tag">'24: ${item.cut_2024}</span>
                                    <span class="year-tag">'23: ${item.cut_2023}</span>
                                </div>
                            </div>
                            ${convertedText}
                            <div class="detail-item"><span>모집인원</span><strong>${item.capacity} 명</strong></div>
                            <div class="detail-item"><span>'25 경쟁률</span><strong>${item.competition_2025} : 1</strong></div>
                            <div class="elem-box"><span>📋 전형 요소 및 평가비율</span><strong>${item.elements}</strong></div>
                            <div class="req-box"><span>⚡ 수시 수능 최저학력기준</span><strong>${item.requirements}</strong></div>
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div class="res-card">
                        <div class="res-header">
                            <div>
                                <div class="res-univ">${item.univ} (${item.group}군) ${tierBadge}</div>
                                <div class="res-region"><i class="fa-solid fa-location-dot"></i> ${item.region}</div>
                            </div>
                            <span class="status-badge ${badgeClass}">${item.status.split(' ')[0]}</span>
                        </div>
                        <div class="res-dept">${item.department}</div>
                        <div class="res-details">
                            <div class="cutoff-3yr-box">
                                <span>3개년 백분위 컷: <strong>${item.cutoff_3yr} 점</strong></span>
                                <div class="cutoff-years">
                                    <span class="year-tag">'25: ${item.cut_2025}</span>
                                    <span class="year-tag">'24: ${item.cut_2024}</span>
                                </div>
                            </div>
                            <div class="detail-item"><span>내 백분위</span><strong>${item.user_percentile} 점</strong></div>
                            <div class="detail-item"><span>모집인원</span><strong>${item.capacity} 명</strong></div>
                            <div class="detail-item"><span>경쟁률</span><strong>${item.competition_2025} : 1</strong></div>
                            <div class="elem-box"><span>📋 전형 요소</span><strong>${item.elements}</strong></div>
                        </div>
                    </div>
                `;
            }
        });
        html += '</div>';

        resultsContainer.innerHTML = html;
    }

    // Initialize UI for GED default mode without auto-running engine on page load
    updateUIForMode('susi-ged');
    
    // Set initial welcome state for results container
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="empty-state" style="padding: 48px 24px; text-align: center;">
                <i class="fa-solid fa-rocket" style="font-size: 48px; color: #818cf8; margin-bottom: 16px;"></i>
                <h3 style="font-size: 18px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;">하바나-트리니티 대입 진단 엔진 준비 완료</h3>
                <p style="font-size: 14.5px; color: #94a3b8; max-width: 500px; margin: 0 auto 20px auto;">성적 및 진단 조건을 확인하신 후 <strong style="color: #c7d2fe;">[🚀 하바나-트리니티 엔진 가동]</strong> 버튼을 누르시면 3개년 합격 추이 기반 소신·적정·안정 분석 결과가 펼쳐집니다.</p>
            </div>
        `;
    }
    if (statusBar) {
        statusBar.style.display = 'none';
    }
});
