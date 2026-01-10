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

## Phase 0: Foundation (2-3 weeks)

### Goal: Set up project structure and shared infrastructure

**Technical Setup**
- [ ] Create `/readingplanet` directory structure
- [ ] Set up shared component library (from FunBookies)
- [ ] Configure build/deploy pipeline
- [ ] Set up staging environment

**Design System**
- [ ] Define color palette (mature, not childish)
- [ ] Typography scale (readable, dyslexia-friendly option)
- [ ] Component library (buttons, cards, inputs)
- [ ] Mobile-first responsive breakpoints

**Shared Services**
- [ ] Port `data-service.js` for IndexedDB storage
- [ ] Port student picker/profile system
- [ ] Port voice recording utilities
- [ ] Set up analytics events

**Deliverable:** Empty shell app with design system, ready for features

---

## Phase 1: Core Reader (4-6 weeks)

### Goal: Students can read texts with basic support

**1.1 Text Display**
- [ ] Clean reader view (no distractions)
- [ ] Font size adjustment (S/M/L/XL)
- [ ] Line spacing options
- [ ] Dark mode / high contrast
- [ ] Progress indicator (% complete)

**1.2 Basic Interactions**
- [ ] Tap word for definition (dictionary API)
- [ ] Highlight text (persisted)
- [ ] Add margin notes
- [ ] Bookmark pages

**1.3 Audio Support**
- [ ] Text-to-speech (Web Speech API)
- [ ] Adjustable speed (0.75x - 1.5x)
- [ ] Read-along highlighting (word by word)
- [ ] Play/pause/restart controls

**1.4 Content Library (Starter)**
- [ ] JSON schema for texts
- [ ] 10 high-interest articles (original)
- [ ] 5 public domain short stories
- [ ] Basic metadata (title, level, word count)
- [ ] Simple browse/search UI

**1.5 Basic Progress**
- [ ] Track reading position
- [ ] Track time spent
- [ ] "Continue reading" on return
- [ ] Simple reading history

**Deliverable:** Working reader with 15+ texts, dictionary, audio, progress tracking

---

## Phase 2: Fluency Module (3-4 weeks)

### Goal: Measure and track oral reading fluency

**2.1 Fluency Passages**
- [ ] Create 20 leveled passages (100-250 words each)
- [ ] 4 levels: grades 3-4, 5-6, 7-8, 9-10
- [ ] High-interest topics (sports, tech, music, etc.)
- [ ] Passage selection by level

**2.2 Timed Reading**
- [ ] 1-minute countdown timer
- [ ] Voice recording during reading
- [ ] "Start/Stop" controls
- [ ] Playback of recording

**2.3 WCPM Calculation**
- [ ] Port WCPM logic from FunBookies read-aloud
- [ ] Word count display
- [ ] Self-report errors (tap words missed)
- [ ] Calculate WCPM score

**2.4 Fluency Progress**
- [ ] WCPM history chart
- [ ] Growth over time visualization
- [ ] Grade-level benchmarks shown
- [ ] Celebration for improvements

**2.5 Repeated Reading**
- [ ] Same passage multiple attempts
- [ ] Compare scores across attempts
- [ ] "Beat your score" motivation

**Deliverable:** Full fluency practice with WCPM tracking and progress visualization

---

## Phase 3: Comprehension Checks (3-4 weeks)

### Goal: Verify understanding during and after reading

**3.1 Check-in Questions**
- [ ] Question bank per text (5-10 questions each)
- [ ] Question types: multiple choice, true/false
- [ ] Triggered every 200-300 words
- [ ] Non-intrusive modal UI

**3.2 Question Quality**
- [ ] Literal comprehension (who, what, when)
- [ ] Inferential (why, how)
- [ ] Vocabulary in context
- [ ] Main idea / summary

**3.3 Feedback & Scaffolding**
- [ ] Immediate right/wrong feedback
- [ ] "Try again" with hint for wrong answers
- [ ] Show correct answer after 2 attempts
- [ ] Link back to relevant text section

**3.4 Comprehension Tracking**
- [ ] Accuracy per text
- [ ] Accuracy by question type
- [ ] Trend over time
- [ ] Skill gap identification

**3.5 AI Question Generation (Stretch)**
- [ ] Generate questions for new texts via Claude
- [ ] Human review workflow
- [ ] Quality scoring

**Deliverable:** All texts have comprehension checks, tracking shows patterns

---

## Phase 4: Student Profiles & Progress (2-3 weeks)

### Goal: Personalized experience with visible growth

**4.1 Student Onboarding**
- [ ] Name, avatar selection
- [ ] Grade level input
- [ ] Reading preferences (genres)
- [ ] Initial placement (simple or skip)

**4.2 Dashboard**
- [ ] Welcome back + current streak
- [ ] "Continue reading" card
- [ ] Weekly stats (time, words, texts)
- [ ] Recent activity feed

**4.3 Progress Visualization**
- [ ] Reading level growth (Lexile estimate)
- [ ] WCPM growth chart
- [ ] Books/texts completed
- [ ] Time invested

**4.4 Goals & Streaks**
- [ ] Weekly reading time goal
- [ ] Daily streak tracking
- [ ] Goal celebration
- [ ] Streak recovery (pause, not lose)

**4.5 Recommendations**
- [ ] "Next up for you" based on level + interests
- [ ] "Because you liked X" suggestions
- [ ] New arrivals in favorite genres

**Deliverable:** Personalized student experience with clear progress visibility

---

## Phase 5: Vocabulary System (3-4 weeks)

### Goal: Build vocabulary through reading context

**5.1 Word Collection**
- [ ] "Save word" from reader
- [ ] Auto-collect looked-up words
- [ ] Personal word bank
- [ ] Word details (definition, pronunciation, example)

**5.2 Pre-Reading Vocabulary**
- [ ] Key words listed before each text
- [ ] Visual + audio + definition
- [ ] Quick check (use in sentence)
- [ ] Words appear highlighted in text

**5.3 Practice Modes**
- [ ] Flashcards with spaced repetition
- [ ] Definition matching
- [ ] Fill-in-the-blank (context)
- [ ] Use it in a sentence

**5.4 Vocabulary Progress**
- [ ] Words learned count
- [ ] Mastery levels (learning → known → mastered)
- [ ] Review queue (due for practice)
- [ ] Word map visualization

**5.5 Morphology (Stretch)**
- [ ] Prefix/suffix/root breakdown
- [ ] Word family connections
- [ ] Build words from parts

**Deliverable:** Complete vocabulary learning loop integrated with reading

---

## Phase 6: Writing Studio (4-5 weeks)

### Goal: Practice written comprehension with AI feedback

**6.1 Writing Prompts**
- [ ] Summary prompts (per text)
- [ ] Response prompts (opinion, connection)
- [ ] Prompt bank with difficulty levels
- [ ] Prompts appear after reading

**6.2 Writing Interface**
- [ ] Clean text editor
- [ ] Word count display
- [ ] Reference back to text
- [ ] Save draft functionality

**6.3 AI Feedback (Claude)**
- [ ] Submit for feedback
- [ ] Scoring rubric (main idea, evidence, organization, mechanics)
- [ ] Specific improvement suggestions
- [ ] Highlight strengths

**6.4 Revision Flow**
- [ ] View feedback on draft
- [ ] Edit and resubmit
- [ ] Compare versions
- [ ] Track improvement

**6.5 Writing Portfolio**
- [ ] All submissions saved
- [ ] Growth comparison (early vs. recent)
- [ ] Best work showcase
- [ ] Export option

**Deliverable:** Full writing practice loop with AI feedback and revision

---

## Phase 7: Teacher Dashboard (4-5 weeks)

### Goal: Teachers can monitor and support students

**7.1 Class Management**
- [ ] Create class / add students
- [ ] Class code join
- [ ] Import from CSV
- [ ] Student list view

**7.2 Class Overview**
- [ ] Class averages (level, WCPM, time)
- [ ] Activity summary (who's active, who's not)
- [ ] Alerts (struggling, inactive)
- [ ] Quick filters (needs help, on track, exceeding)

**7.3 Individual Student View**
- [ ] Full progress report
- [ ] Reading history
- [ ] Skill breakdown
- [ ] Writing submissions
- [ ] Recommendations

**7.4 Assignments**
- [ ] Assign specific texts
- [ ] Assign writing prompts
- [ ] Due dates
- [ ] Completion tracking

**7.5 Reports**
- [ ] Class progress report (PDF)
- [ ] Individual student report
- [ ] Growth over time
- [ ] Standards alignment (stretch)

**Deliverable:** Teachers can manage classes and track all student progress

---

## Phase 8: Adaptive Learning (4-6 weeks)

### Goal: Personalized pathways based on skill gaps

**8.1 Diagnostic Assessment**
- [ ] Initial placement test
- [ ] Adaptive question selection
- [ ] Estimate Lexile level
- [ ] Identify skill gaps

**8.2 Skills Practice Modules**
- [ ] Comprehension skills (main idea, inference, etc.)
- [ ] Vocabulary skills (context clues, word parts)
- [ ] Basic decoding (for severe gaps)
- [ ] Grammar/syntax

**8.3 Adaptive Pathways**
- [ ] Recommend practice based on gaps
- [ ] Adjust text recommendations by level
- [ ] Progress through skill sequences
- [ ] Mastery gates

**8.4 FunBookies Bridge**
- [ ] Detect phonics gaps
- [ ] Link to FunBookies activities
- [ ] Shared progress tracking
- [ ] Seamless transition

**8.5 Periodic Reassessment**
- [ ] Monthly skill checks
- [ ] Update level estimates
- [ ] Adjust recommendations
- [ ] Growth reporting

**Deliverable:** Fully adaptive experience that meets students where they are

---

## Phase 9: Engagement & Gamification (2-3 weeks)

### Goal: Motivate consistent practice

**9.1 XP System**
- [ ] Earn XP for activities
- [ ] Level progression
- [ ] Level names (Reader → Master)
- [ ] Level-up celebrations

**9.2 Badges/Achievements**
- [ ] Milestone badges (first book, 10k words, etc.)
- [ ] Skill badges (fluency, vocabulary)
- [ ] Streak badges
- [ ] Badge display on profile

**9.3 Streaks & Goals**
- [ ] Daily streak counter
- [ ] Streak freeze (pause without losing)
- [ ] Weekly goals (customizable)
- [ ] Goal celebration

**9.4 Leaderboards (Optional)**
- [ ] Class-only leaderboards
- [ ] Opt-in participation
- [ ] Multiple categories (time, books, growth)
- [ ] Teacher controls

**Deliverable:** Engaging progression system without being childish

---

## Phase 10: Content Expansion (Ongoing)

### Goal: Build compelling library

**10.1 Text Acquisition**
- [ ] License high-interest novels (excerpts)
- [ ] Partner with authors/publishers
- [ ] Commission original content
- [ ] Curate public domain

**10.2 Content Pipeline**
- [ ] Editorial workflow
- [ ] Lexile analysis
- [ ] Vocabulary tagging
- [ ] Question creation
- [ ] Audio recording

**10.3 Library Growth Targets**
| Quarter | Texts | Fluency Passages |
|---------|-------|------------------|
| Q1      | 50    | 30               |
| Q2      | 100   | 60               |
| Q3      | 200   | 100              |
| Q4      | 400   | 150              |

**10.4 Content Types**
- [ ] Articles (news, science, sports)
- [ ] Short stories
- [ ] Novel excerpts
- [ ] Graphic texts
- [ ] Poetry
- [ ] Plays/scripts

**Deliverable:** Growing library that keeps students engaged

---

## Phase 11: Integrations (3-4 weeks)

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

| Phase | Name | Duration | Key Deliverable |
|-------|------|----------|-----------------|
| 0 | Foundation | 2-3 weeks | Project setup, design system |
| 1 | Core Reader | 4-6 weeks | Working reader with 15+ texts |
| 2 | Fluency | 3-4 weeks | WCPM tracking and practice |
| 3 | Comprehension | 3-4 weeks | Check-ins for all texts |
| 4 | Profiles & Progress | 2-3 weeks | Student dashboard |
| 5 | Vocabulary | 3-4 weeks | Word learning system |
| 6 | Writing | 4-5 weeks | AI-powered writing feedback |
| 7 | Teacher Dashboard | 4-5 weeks | Class management & reports |
| 8 | Adaptive Learning | 4-6 weeks | Personalized pathways |
| 9 | Gamification | 2-3 weeks | XP, badges, streaks |
| 10 | Content | Ongoing | Library expansion |
| 11 | Integrations | 3-4 weeks | SSO, LMS, data sync |

**Total estimated: ~9-12 months to full product**

---

## MVP Definition

### Minimum for Pilot (Phases 0-4)
**~3-4 months of work**

What's included:
- Reader with 15-20 texts
- Dictionary, audio, annotations
- Fluency measurement (WCPM)
- Comprehension check-ins
- Student progress tracking
- Basic gamification (streaks)

What's NOT included:
- Writing/AI feedback
- Teacher dashboard
- Adaptive pathways
- LMS integrations

**Good enough to:** Test with 1-2 classrooms, validate core experience

---

### Pilot-Ready (Phases 0-7)
**~6-8 months of work**

Adds:
- Vocabulary system
- Writing with AI feedback
- Teacher dashboard
- 50+ texts

**Good enough to:** Pilot with 5-10 schools

---

### Full Product (All Phases)
**~9-12 months of work**

Adds:
- Adaptive learning
- Full gamification
- 200+ texts
- School integrations

**Good enough to:** Commercial launch

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
1. **Target grade range?** 4-8 vs 6-10 vs 4-10?
2. **Pricing model?** Freemium, per-student, site license?
3. **Content strategy?** Original-first vs license-first?
4. **Technical stack?** React vs Vue? Separate app vs FunBookies extension?

### After Phase 1
1. **Double down on reader or add fluency?**
2. **Content quantity vs features?**
3. **Seek pilot schools?**

### After MVP (Phase 4)
1. **Ready for pilots?**
2. **Which Phase 5-7 is highest priority?**
3. **Hire content creators?**

---

## Next Actions

1. **Decide target grade range** - impacts content, design, vocabulary
2. **Create project structure** - `/readingplanet` directory
3. **Design core reader UI** - mockups before code
4. **Source first 10 texts** - what's available, what to create?
5. **Port FunBookies utilities** - voice, progress, student picker
