# Curriculum Platform Competitor Plan

## Executive Summary

Build a K-12 digital curriculum platform that combines high-quality instructional materials with AI-powered teaching tools. Unlike Kiddom's broad approach, we focus initially on **literacy/reading intervention** (leveraging ReadingPlanet + FunBookies), then expand to full ELA curriculum.

**Positioning:** "The reading intervention platform that grows into your core curriculum"

---

## Market Analysis

### Kiddom Strengths
- Bundled HQIM curriculum + delivery platform
- Strong EdReports-rated curriculum partners
- Teacher-facing AI saves grading time
- Free tier drives adoption
- Standards mastery tracking

### Kiddom Weaknesses
- **Opaque pricing** - schools can't self-serve
- **Generic platform** - not specialized for any subject
- **No adaptive learning** - same content for all students
- **Dependent on partners** - doesn't own curriculum IP
- **No intervention focus** - assumes grade-level readers

### Our Advantages
1. **Own the content** - FunBookies phonics, ReadingPlanet texts
2. **Adaptive from day one** - diagnostic → personalized pathway
3. **Intervention expertise** - designed for struggling readers
4. **Transparent pricing** - self-serve for teachers, clear district pricing
5. **FunBookies → ReadingPlanet bridge** - K-2 to 4-10 pipeline

---

## Product Strategy

### Phase 1: Reading Intervention Platform (Current)
**ReadingPlanet as standalone intervention tool**

Already built:
- Core reader with dictionary, audio, annotations
- Fluency practice with WCPM tracking
- Comprehension checks
- Vocabulary system with spaced repetition
- Writing studio with AI feedback
- Teacher dashboard
- Adaptive learning with diagnostic
- Gamification (XP, badges, streaks)
- Content editor with AI tools

Gap to close:
- [ ] Standards alignment on all content
- [ ] Mastery tracking by standard
- [ ] LMS integrations (Clever, ClassLink, Google Classroom)
- [ ] More content (50+ texts)

### Phase 2: Curriculum Delivery Platform
**Add curriculum management features**

New features:
- [ ] Planner (curriculum organization)
- [ ] Timeline (assignment calendar)
- [ ] Playlists (differentiation pathways)
- [ ] Pacing guides
- [ ] Curriculum editing suite
- [ ] District-level curriculum management
- [ ] Grade passback to LMS

### Phase 3: Full ELA Curriculum
**Partner with or create ELA curriculum**

Options:
1. Partner with OER curriculum (EL Education, etc.)
2. Build original curriculum (expensive, slow)
3. Hybrid: Partner + original intervention content

New features:
- [ ] Full K-8 ELA scope & sequence
- [ ] Unit/lesson structure
- [ ] Teacher editions
- [ ] Print materials option
- [ ] Professional development content

### Phase 4: Multi-Subject Expansion
**Expand beyond ELA**

Candidates:
- Math (partner with IM or build)
- Science (OpenSciEd integration)
- Social Studies

---

## Technical Architecture

### Current Stack (Keep)
```
Frontend: Vanilla JS, HTML, CSS
Storage: IndexedDB (client-side)
Hosting: Static files (Netlify/Vercel)
AI: Claude API (simulated currently)
```

### Additions Needed

#### Authentication & Rostering
```
- Google SSO
- Clever integration
- ClassLink integration
- Manual accounts with email verification
```

#### Backend Services (New)
```
- User management service
- Class/roster management
- Curriculum content API
- Assessment data API
- Reporting/analytics API
- AI feedback service (Claude)
```

#### Database
```
- PostgreSQL for relational data
- Redis for caching/sessions
- S3 for content storage
```

#### Infrastructure
```
- API server (Node.js or Python)
- Background job processing
- CDN for content delivery
- Analytics pipeline
```

### Data Model

```
Districts
  └── Schools
       └── Teachers
            └── Classes
                 └── Students
                      └── Progress
                      └── Assignments
                      └── Assessments

Curriculum
  └── Courses
       └── Units
            └── Lessons
                 └── Activities
                      └── Questions
                      └── Resources

Standards
  └── Standard Sets (CCSS, State)
       └── Domains
            └── Standards
                 └── Skills
```

---

## Feature Roadmap

### Q1: Foundation (Integrations + Standards)

#### 1.1 Authentication System
- [ ] Email/password accounts
- [ ] Google SSO
- [ ] Clever rostering
- [ ] ClassLink rostering
- [ ] Role management (student, teacher, admin, district)

#### 1.2 Standards Framework
- [ ] Import CCSS ELA standards
- [ ] Standards tagging on all content
- [ ] Mastery tracking by standard
- [ ] Standards-based reporting
- [ ] Max Value Grading option

#### 1.3 LMS Integration
- [ ] Google Classroom roster sync
- [ ] Canvas grade passback
- [ ] Schoology integration
- [ ] Assignment deep links

#### 1.4 Content Expansion
- [ ] 50 library texts (various genres/levels)
- [ ] 50 fluency passages
- [ ] All content tagged to standards
- [ ] Lexile levels verified

### Q2: Curriculum Tools

#### 2.1 Planner
- [ ] Curriculum organization (units, lessons)
- [ ] Drag-drop interface
- [ ] Resource library integration
- [ ] Sharing between teachers
- [ ] Master curriculum (district level)

#### 2.2 Timeline
- [ ] Calendar view of assignments
- [ ] Drag assignments to dates
- [ ] Student view of upcoming work
- [ ] Due date management
- [ ] Pacing guide overlay

#### 2.3 Playlists
- [ ] Create differentiation pathways
- [ ] Assign to individuals/groups
- [ ] Track completion
- [ ] AI-suggested playlists based on gaps

#### 2.4 Enhanced Assignments
- [ ] 15+ question types
- [ ] Auto-grading for objective questions
- [ ] AI-assisted grading for open-ended
- [ ] Rubric builder
- [ ] Peer review option

### Q3: AI Features

#### 3.1 Teacher AI Tools
- [ ] Lesson summarizer
- [ ] Practice generator
- [ ] Question generator
- [ ] Feedback generator
- [ ] Lesson clipper (condense lessons)

#### 3.2 Predictive Analytics
- [ ] At-risk student identification
- [ ] Skill gap prediction
- [ ] Recommended interventions
- [ ] Growth forecasting

#### 3.3 Smart Grouping
- [ ] Auto-group by misconception
- [ ] Flexible grouping suggestions
- [ ] Group performance tracking

#### 3.4 Reporting Enhancements
- [ ] District-level dashboards
- [ ] Growth over time visualizations
- [ ] Comparative analytics
- [ ] Custom report builder

### Q4: Scale & Polish

#### 4.1 District Features
- [ ] District admin dashboard
- [ ] Curriculum approval workflow
- [ ] Teacher usage analytics
- [ ] Bulk student management
- [ ] Data export API

#### 4.2 Professional Development
- [ ] Embedded PD content
- [ ] Implementation guides
- [ ] Video tutorials
- [ ] Certification tracking

#### 4.3 Parent Portal
- [ ] Progress visibility
- [ ] Assignment notifications
- [ ] Communication tools
- [ ] Home practice suggestions

#### 4.4 Mobile Apps
- [ ] iOS app
- [ ] Android app
- [ ] Offline mode for content

---

## Question Types to Build

### Auto-Graded
| Type | Description | Priority |
|------|-------------|----------|
| Multiple Choice | Single/multi-select | P0 (Have) |
| True/False | Binary choice | P0 (Have) |
| Fill in Blank | Text input, exact match | P1 |
| Ordering | Drag to sequence | P1 |
| Matching | Drag to match pairs | P1 |
| Categorization | Sort into groups | P2 |
| Hot Spot | Click correct area | P2 |

### AI-Assisted Grading
| Type | Description | Priority |
|------|-------------|----------|
| Short Answer | 1-2 sentence response | P1 |
| Extended Response | Paragraph+ response | P0 (Have) |
| Evidence-Based | Quote + explain | P1 |

### Creative Response
| Type | Description | Priority |
|------|-------------|----------|
| Drawing | Sketch/annotate | P2 |
| Audio Recording | Voice response | P0 (Have) |
| Video Recording | Video response | P3 |
| File Upload | Document submission | P2 |

---

## Pricing Strategy

### Tier 1: Free (Individual Teachers)
- Unlimited students
- Core reader + library (10 texts)
- Basic progress tracking
- Limited AI features (5/month)
- Community support

### Tier 2: Pro ($8/student/year)
- Full library access (all texts)
- Standards mastery tracking
- All AI features
- LMS integration
- Email support

### Tier 3: School ($12/student/year)
- Everything in Pro
- Admin dashboard
- Curriculum tools (Planner, Timeline)
- Usage analytics
- Phone support
- PD resources

### Tier 4: District (Custom pricing)
- Everything in School
- District dashboard
- Curriculum editing suite
- API access
- Dedicated support
- Custom implementation
- Data warehouse integration

### Comparison to Kiddom
| Feature | Us | Kiddom |
|---------|-----|--------|
| Transparent pricing | Yes | No (quote only) |
| Free tier | Yes (generous) | Yes (limited) |
| Self-serve purchase | Yes | No |
| Intervention focus | Yes | No |
| Adaptive learning | Yes | Limited |

---

## Go-to-Market Strategy

### Phase 1: Intervention Niche
**Target:** Title I schools, reading specialists, intervention teachers

1. Free tier drives adoption
2. Case studies with struggling reader outcomes
3. Partner with reading intervention organizations
4. Conference presence (ILA, LDA)
5. SEO for "reading intervention software"

### Phase 2: Expand to Core ELA
**Target:** Schools using intervention, looking to consolidate

1. Upsell intervention users to full platform
2. Curriculum partnership announcements
3. EdReports submission (if partnering)
4. District pilot programs

### Phase 3: Multi-District Scale
**Target:** Large districts seeking unified platform

1. Reference customers from Phase 2
2. State adoption list applications
3. RFP response capability
4. Implementation services

---

## Competitive Moat

### 1. Owned Content
- FunBookies phonics library
- ReadingPlanet texts
- Original intervention materials
- Not dependent on partners

### 2. Adaptive Engine
- Diagnostic assessment
- Personalized pathways
- Skill gap detection
- FunBookies bridge for decoding gaps

### 3. K-10 Pipeline
- FunBookies (K-2) → ReadingPlanet (4-10)
- Continuous progress tracking
- Family relationship across products

### 4. AI-First Design
- Built with AI from start (not bolted on)
- Teacher-facing for privacy
- Feedback quality as differentiator

### 5. Transparent Business Model
- Clear pricing builds trust
- Self-serve reduces sales friction
- Free tier proves value before purchase

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Curriculum quality questioned | Medium | High | EdReports submission, efficacy studies |
| Kiddom lowers prices | Medium | Medium | Differentiate on intervention/adaptive |
| LMS builds curriculum features | Low | High | Focus on specialized reading, not generic LMS |
| Content licensing costs | Low | Medium | Own content, use public domain |
| AI feedback quality issues | Medium | High | Human review layer, teacher approval |
| School budget cuts | Medium | Medium | Free tier maintains presence |

---

## Success Metrics

### Year 1
- 1,000 active teachers (free + paid)
- 50 paying schools
- 10,000 active students
- 100 texts in library
- CCSS ELA standards mapped

### Year 2
- 5,000 active teachers
- 200 paying schools
- 50,000 active students
- 10 district contracts
- Full curriculum tools launched

### Year 3
- 15,000 active teachers
- 500 paying schools
- 150,000 active students
- 50 district contracts
- Multi-subject expansion begun

---

## Immediate Next Steps

1. **Standards Integration** - Add CCSS ELA tagging to all ReadingPlanet content
2. **Authentication** - Build Google SSO + Clever integration
3. **Content Sprint** - Reach 50 texts with standards alignment
4. **Mastery Tracking** - Implement max-value grading by standard
5. **Pricing Page** - Launch transparent pricing with self-serve signup
6. **Pilot Schools** - Recruit 5 intervention teachers for beta

---

## Team Needs

### Immediate (Build MVP)
- 1 Full-stack developer (auth, API)
- 1 Frontend developer (curriculum tools)
- 1 Content creator (texts, questions)

### Growth Phase
- 1 DevOps/Infrastructure
- 1 AI/ML engineer
- 2 Content creators
- 1 Customer success
- 1 Sales (district focus)

### Scale Phase
- Implementation specialists
- Professional development team
- Expanded content team
- Enterprise sales team
