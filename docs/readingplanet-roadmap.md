# ReadingPlanet Roadmap

## Strategic Context

### Why ReadingPlanet?
- FunBookies serves K-2, but struggling readers in grades 4-10 need intervention too
- iLit costs ~$40/student/year - opportunity for affordable alternative
- FunBookies infrastructure (voice, progress tracking) can be reused
- Natural upsell path: FunBookies families → ReadingPlanet as kids grow

### Success Criteria
- **Educational:** 1+ year reading growth per school year
- **Engagement:** 80% of students use 3+ days/week
- **Business:** 10 pilot schools in first semester

---

## Phase 0: Foundation ✅ COMPLETE

### Goal: Set up project structure and shared infrastructure

**Technical Setup**
- [x] Create `/readingplanet` directory structure
- [x] Set up shared component library (from FunBookies)
- [x] Configure build/deploy pipeline
- [x] Set up staging environment

**Design System**
- [x] Define color palette (mature, not childish)
- [x] Typography scale (readable, dyslexia-friendly option)
- [x] Component library (buttons, cards, inputs)
- [x] Mobile-first responsive breakpoints

**Shared Services**
- [x] Port `data-service.js` for IndexedDB storage
- [x] Port student picker/profile system
- [x] Port voice recording utilities
- [x] Set up analytics events

**Deliverable:** Empty shell app with design system, ready for features

---

## Phase 1: Core Reader ✅ COMPLETE

### Goal: Students can read texts with basic support

**1.1 Text Display**
- [x] Clean reader view (no distractions)
- [x] Font size adjustment (S/M/L/XL)
- [x] Line spacing options
- [x] Dark mode / high contrast
- [x] Progress indicator (% complete)

**1.2 Basic Interactions**
- [x] Tap word for definition (dictionary API)
- [x] Highlight text (persisted)
- [x] Add margin notes
- [x] Bookmark pages

**1.3 Audio Support**
- [x] Text-to-speech (Web Speech API)
- [x] Adjustable speed (0.75x - 1.5x)
- [x] Read-along highlighting (word by word)
- [x] Play/pause/restart controls

**1.4 Content Library (Starter)**
- [x] JSON schema for texts
- [x] 10 high-interest articles (original)
- [x] 5 public domain short stories
- [x] Basic metadata (title, level, word count)
- [x] Simple browse/search UI

**1.5 Basic Progress**
- [x] Track reading position
- [x] Track time spent
- [x] "Continue reading" on return
- [x] Simple reading history

**Deliverable:** Working reader with 15+ texts, dictionary, audio, progress tracking

---

## Phase 2: Fluency Module ✅ COMPLETE

### Goal: Measure and track oral reading fluency

**2.1 Fluency Passages**
- [x] Create 20 leveled passages (100-250 words each)
- [x] 4 levels: grades 3-4, 5-6, 7-8, 9-10
- [x] High-interest topics (sports, tech, music, etc.)
- [x] Passage selection by level

**2.2 Timed Reading**
- [x] 1-minute countdown timer
- [x] Voice recording during reading
- [x] "Start/Stop" controls
- [x] Playback of recording

**2.3 WCPM Calculation**
- [x] Port WCPM logic from FunBookies read-aloud
- [x] Word count display
- [x] Self-report errors (tap words missed)
- [x] Calculate WCPM score

**2.4 Fluency Progress**
- [x] WCPM history chart
- [x] Growth over time visualization
- [x] Grade-level benchmarks shown
- [x] Celebration for improvements

**2.5 Repeated Reading**
- [x] Same passage multiple attempts
- [x] Compare scores across attempts
- [x] "Beat your score" motivation

**Deliverable:** Full fluency practice with WCPM tracking and progress visualization

---

## Phase 3: Comprehension Checks ✅ COMPLETE

### Goal: Verify understanding during and after reading

**3.1 Check-in Questions**
- [x] Question bank per text (5-10 questions each)
- [x] Question types: multiple choice, true/false
- [x] Triggered every 200-300 words
- [x] Non-intrusive modal UI

**3.2 Question Quality**
- [x] Literal comprehension (who, what, when)
- [x] Inferential (why, how)
- [x] Vocabulary in context
- [x] Main idea / summary

**3.3 Feedback & Scaffolding**
- [x] Immediate right/wrong feedback
- [x] "Try again" with hint for wrong answers
- [x] Show correct answer after 2 attempts
- [x] Link back to relevant text section

**3.4 Comprehension Tracking**
- [x] Accuracy per text
- [x] Accuracy by question type
- [x] Trend over time
- [x] Skill gap identification

**3.5 AI Question Generation (Stretch)**
- [x] Generate questions for new texts via Claude
- [x] Human review workflow
- [x] Quality scoring

**Deliverable:** All texts have comprehension checks, tracking shows patterns

---

## Phase 4: Student Profiles & Progress ✅ COMPLETE

### Goal: Personalized experience with visible growth

**4.1 Student Onboarding**
- [x] Name, avatar selection
- [x] Grade level input
- [x] Reading preferences (genres)
- [x] Initial placement (simple or skip)

**4.2 Dashboard**
- [x] Welcome back + current streak
- [x] "Continue reading" card
- [x] Weekly stats (time, words, texts)
- [x] Recent activity feed

**4.3 Progress Visualization**
- [x] Reading level growth (Lexile estimate)
- [x] WCPM growth chart
- [x] Books/texts completed
- [x] Time invested

**4.4 Goals & Streaks**
- [x] Weekly reading time goal
- [x] Daily streak tracking
- [x] Goal celebration
- [x] Streak recovery (pause, not lose)

**4.5 Recommendations**
- [x] "Next up for you" based on level + interests
- [x] "Because you liked X" suggestions
- [x] New arrivals in favorite genres

**Deliverable:** Personalized student experience with clear progress visibility

---

## Phase 5: Vocabulary System ✅ COMPLETE

### Goal: Build vocabulary through reading context

**5.1 Word Collection**
- [x] "Save word" from reader
- [x] Auto-collect looked-up words
- [x] Personal word bank
- [x] Word details (definition, pronunciation, example)

**5.2 Pre-Reading Vocabulary**
- [x] Key words listed before each text
- [x] Visual + audio + definition
- [x] Quick check (use in sentence)
- [x] Words appear highlighted in text

**5.3 Practice Modes**
- [x] Flashcards with spaced repetition
- [x] Definition matching
- [x] Fill-in-the-blank (context)
- [x] Use it in a sentence

**5.4 Vocabulary Progress**
- [x] Words learned count
- [x] Mastery levels (learning → known → mastered)
- [x] Review queue (due for practice)
- [x] Word map visualization

**5.5 Morphology (Stretch)**
- [x] Prefix/suffix/root breakdown
- [x] Word family connections
- [x] Build words from parts

**Deliverable:** Complete vocabulary learning loop integrated with reading

---

## Phase 6: Writing Studio ✅ COMPLETE

### Goal: Practice written comprehension with AI feedback

**6.1 Writing Prompts**
- [x] Summary prompts (per text)
- [x] Response prompts (opinion, connection)
- [x] Prompt bank with difficulty levels
- [x] Prompts appear after reading

**6.2 Writing Interface**
- [x] Clean text editor
- [x] Word count display
- [x] Reference back to text
- [x] Save draft functionality

**6.3 AI Feedback (Claude)**
- [x] Submit for feedback
- [x] Scoring rubric (main idea, evidence, organization, mechanics)
- [x] Specific improvement suggestions
- [x] Highlight strengths

**6.4 Revision Flow**
- [x] View feedback on draft
- [x] Edit and resubmit
- [x] Compare versions
- [x] Track improvement

**6.5 Writing Portfolio**
- [x] All submissions saved
- [x] Growth comparison (early vs. recent)
- [x] Best work showcase
- [x] Export option

**Deliverable:** Full writing practice loop with AI feedback and revision

---

## Phase 7: Teacher Dashboard ✅ COMPLETE

### Goal: Teachers can monitor and support students

**7.1 Class Management**
- [x] Create class / add students
- [x] Class code join
- [x] Import from CSV
- [x] Student list view

**7.2 Class Overview**
- [x] Class averages (level, WCPM, time)
- [x] Activity summary (who's active, who's not)
- [x] Alerts (struggling, inactive)
- [x] Quick filters (needs help, on track, exceeding)

**7.3 Individual Student View**
- [x] Full progress report
- [x] Reading history
- [x] Skill breakdown
- [x] Writing submissions
- [x] Recommendations

**7.4 Assignments**
- [x] Assign specific texts
- [x] Assign writing prompts
- [x] Due dates
- [x] Completion tracking

**7.5 Reports**
- [x] Class progress report (PDF)
- [x] Individual student report
- [x] Growth over time
- [x] Standards alignment (stretch)

**Deliverable:** Teachers can manage classes and track all student progress

---

## Phase 8: Adaptive Learning ✅ COMPLETE

### Goal: Personalized pathways based on skill gaps

**8.1 Diagnostic Assessment**
- [x] Initial placement test
- [x] Adaptive question selection
- [x] Estimate Lexile level
- [x] Identify skill gaps

**8.2 Skills Practice Modules**
- [x] Comprehension skills (main idea, inference, etc.)
- [x] Vocabulary skills (context clues, word parts)
- [x] Basic decoding (for severe gaps)
- [x] Grammar/syntax

**8.3 Adaptive Pathways**
- [x] Recommend practice based on gaps
- [x] Adjust text recommendations by level
- [x] Progress through skill sequences
- [x] Mastery gates

**8.4 FunBookies Bridge**
- [x] Detect phonics gaps
- [x] Link to FunBookies activities
- [x] Shared progress tracking
- [x] Seamless transition

**8.5 Periodic Reassessment**
- [x] Monthly skill checks
- [x] Update level estimates
- [x] Adjust recommendations
- [x] Growth reporting

**Deliverable:** Fully adaptive experience that meets students where they are

---

## Phase 9: Engagement & Gamification ✅ COMPLETE

### Goal: Motivate consistent practice

**9.1 XP System**
- [x] Earn XP for activities
- [x] Level progression
- [x] Level names (Reader → Master)
- [x] Level-up celebrations

**9.2 Badges/Achievements**
- [x] Milestone badges (first book, 10k words, etc.)
- [x] Skill badges (fluency, vocabulary)
- [x] Streak badges
- [x] Badge display on profile

**9.3 Streaks & Goals**
- [x] Daily streak counter
- [x] Streak freeze (pause without losing)
- [x] Weekly goals (customizable)
- [x] Goal celebration

**9.4 Leaderboards (Optional)**
- [x] Class-only leaderboards
- [x] Opt-in participation
- [x] Multiple categories (time, books, growth)
- [x] Teacher controls

**Deliverable:** Engaging progression system without being childish

---

## Phase 10: Content Expansion ✅ COMPLETE (Initial)

### Goal: Build compelling library

**10.1 Text Acquisition**
- [x] License high-interest novels (excerpts)
- [ ] Partner with authors/publishers
- [x] Commission original content
- [x] Curate public domain

**10.2 Content Pipeline**
- [x] Editorial workflow (content editor tool)
- [x] Lexile analysis
- [x] Vocabulary tagging
- [x] Question creation
- [ ] Audio recording

**10.3 Library Growth Targets**
| Quarter | Texts | Fluency Passages |
|---------|-------|------------------|
| Q1      | 50    | 30 ✅            |
| Q2      | 100   | 60               |
| Q3      | 200   | 100              |
| Q4      | 400   | 150              |

**Current:** 10 texts, 30 fluency passages

**10.4 Content Types**
- [x] Articles (news, science, sports)
- [x] Short stories
- [ ] Novel excerpts
- [ ] Graphic texts
- [x] Poetry
- [ ] Plays/scripts

**Deliverable:** Growing library that keeps students engaged

---

## Phase 11: Integrations (TODO)

### Goal: Fit into school ecosystems

**11.1 Authentication**
- [ ] Google SSO
- [ ] Clever integration
- [ ] ClassLink
- [ ] Manual accounts

**11.2 LMS Integration**
- [ ] Google Classroom (roster sync)
- [ ] Canvas (grades, assignments)
- [ ] Schoology
- [ ] Assignment links

**11.3 Data Import**
- [ ] NWEA MAP scores
- [ ] STAR reading scores
- [ ] i-Ready levels
- [ ] CSV import

**11.4 Reporting Export**
- [ ] PDF reports
- [ ] CSV data export
- [ ] API for district dashboards

**Deliverable:** Seamless integration with school systems

---

## Milestone Summary

| Phase | Name | Status | Key Deliverable |
|-------|------|--------|-----------------|
| 0 | Foundation | ✅ Complete | Project setup, design system |
| 1 | Core Reader | ✅ Complete | Working reader with 15+ texts |
| 2 | Fluency | ✅ Complete | WCPM tracking and practice |
| 3 | Comprehension | ✅ Complete | Check-ins for all texts |
| 4 | Profiles & Progress | ✅ Complete | Student dashboard |
| 5 | Vocabulary | ✅ Complete | Word learning system |
| 6 | Writing | ✅ Complete | AI-powered writing feedback |
| 7 | Teacher Dashboard | ✅ Complete | Class management & reports |
| 8 | Adaptive Learning | ✅ Complete | Personalized pathways |
| 9 | Gamification | ✅ Complete | XP, badges, streaks |
| 10 | Content | ✅ Initial | Library expansion tools |
| 11 | Integrations | 🔲 TODO | SSO, LMS, data sync |

---

## Current Status

**Phases 0-10 Complete!** ReadingPlanet is feature-complete for pilot deployment.

### What's Built:
- Full reader with dictionary, audio, annotations
- Fluency practice with WCPM tracking (30 passages)
- Comprehension checks on all texts
- Student dashboard with progress visualization
- Vocabulary system with spaced repetition
- Writing studio with AI feedback
- Teacher dashboard with class management
- Adaptive learning with diagnostic assessment
- Gamification (XP, badges, streaks, leaderboards)
- Content editor with AI tools
- Library with 10 texts across 7 genres

### Next Steps:
1. **Content:** Add more texts to reach 50+ for Q1
2. **Testing:** User testing with target students
3. **Integrations:** Google SSO, Clever, LMS connections
4. **Pilot:** Deploy to 1-2 classrooms for validation

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Content licensing expensive | Medium | High | Start with public domain + original |
| AI feedback quality issues | Medium | High | Human review layer, iterate prompts |
| Students find it "babyish" | Medium | High | User testing with target age, mature design |
| Teachers don't adopt | Medium | High | Teacher co-design, minimal friction |
| WCPM accuracy problems | Low | Medium | Calibrate against human scoring |
| Scope creep | High | Medium | Strict MVP definition, say no |

---

## Decision Points

### Before Starting
1. **Target grade range?** 4-8 vs 6-10 vs 4-10? ✅ Decided: 4-10
2. **Pricing model?** Freemium, per-student, site license?
3. **Content strategy?** Original-first vs license-first? ✅ Decided: Original-first
4. **Technical stack?** React vs Vue? Separate app vs FunBookies extension? ✅ Decided: Vanilla JS, separate app

### After Phase 1
1. **Double down on reader or add fluency?** ✅ Added fluency
2. **Content quantity vs features?** ✅ Features first, content ongoing
3. **Seek pilot schools?**

### After MVP (Phase 4)
1. **Ready for pilots?** ✅ Yes, after Phase 10
2. **Which Phase 5-7 is highest priority?** ✅ All completed
3. **Hire content creators?**
