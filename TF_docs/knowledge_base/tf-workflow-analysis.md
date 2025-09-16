# TF (Tracks & Fields) Workflow Analysis & Agent Architecture

## Executive Summary
Tracks & Fields is a music licensing and production agency that requires a sophisticated multi-agent system to handle the complex workflow of finding, clearing, and delivering music for advertising and media clients. The workflow involves multiple stages from initial client contact through final delivery, with specialized agents handling different aspects of the process.

## Core Business Model
TF helps brands and agencies:
- Find and license existing music tracks
- Produce custom/bespoke music
- Clear rights and negotiate fees
- Manage the entire music supervision process

## Project Types & Budget Structure

### Project Categories
1. **Synch A-Type**: Above $100k
   - Full service with custom mailouts to labels/publishers
   - Management oversight required
   - Extensive clearance negotiations
   
2. **Synch B-Type**: Above $25k (or $10k, TBD)
   - Playlist/request with custom mailouts
   - Music team and PM collaboration
   
3. **Synch C-Type**: Below $25k (or $10k, TBD)
   - Request-first approach
   - Simplified workflow
   - TBC checking where needed
   
4. **Production Projects**
   - Custom music creation
   - Composer selection and briefing
   - Singer casting through member community

### Margin Structure
- $0-1,500: 100% margin (Library Blanket Deals)
- $1,500-30,000: 50% margin
- $30,000-100,000: 25% margin
- $100,000-250,000: 20% margin
- Above $500,000: 10% margin
- Custom arrangements for specific clients (flat fees, hourly rates)

## Agent Architecture Components

### 1. **Incoming Email Handler Agent**
- **Purpose**: Entry point for all communications
- **Functions**:
  - Classify emails (new project vs. existing project request)
  - Route to appropriate workflow
  - Extract basic metadata
- **Integrations**: Gmail API

### 2. **Brief/Buyout Extractor Agent**
- **Purpose**: Extract structured data from unstructured briefs
- **Extracts**:
  - Client information and sender
  - Brief details (creative, business, technical, contextual)
  - Buyout terms
  - Budget
  - Brand and category
  - Timeline/deadline
- **Challenge**: Briefs are often poorly written and incomplete

### 3. **Project Strategy Head Agent**
- **Purpose**: Strategic project planning
- **Functions**:
  - Determine project type (A/B/C/Production)
  - Translate budget to payout using margin structure
  - Analyze required deliverables
  - Identify missing information
  - Suggest alternative approaches
- **Key Logic**: Budget-to-payout conversion with custom client rules

### 4. **Head of Search Agent (Orchestrator)**
- **Purpose**: Coordinate all search activities
- **Functions**:
  - Determine search types needed (lyrics, similarity, context, etc.)
  - Dispatch to specialized search agents
  - Compile and validate results
  - Ensure proper track identification (Spotify/TF IDs)
- **Manages**: All search sub-agents

### 5. **Specialized Search Agents**

#### 5a. Lyrics Search Agent
- **Purpose**: Find tracks based on lyrics or lyrical sentiment
- **Returns**: List of tracks with Spotify track IDs
- **Integration**: Lyrics database APIs

#### 5b. Reference Search Agent
- **Purpose**: Find similar tracks to references
- **Methods**:
  - TF database lookup
  - YouTube link analysis
  - AIMS similarity matching
- **Integration**: AIMS system, YouTube API

#### 5c. Free Text Search Agent
- **Purpose**: Interpret creative briefs into track searches
- **Technology**: LLM-based interpretation
- **Integration**: ChatGPT/similar

#### 5d. Context/Stats Search Agent
- **Purpose**: Find tracks by specific parameters
- **Criteria**: BPM, key, genre, era, chart performance, etc.
- **Integration**: Music databases

### 6. **Platform Integration Agents**

#### 6a. Spotify Agent
- **Functions**: 
  - Find artist/track IDs
  - Get streaming stats
  - Retrieve track metadata
- **Integration**: Spotify API

#### 6b. Chartmetric Agent
- **Functions**: 
  - Retrieve music analytics
  - Track performance data
  - Artist information
- **Integration**: Chartmetric API (already developed)

#### 6c. TF Platform Agent
- **Functions**:
  - Database queries
  - Playlist creation
  - Track management
  - Member content access
- **Integration**: tracksandfields.com internal API

#### 6d. WF/Odoo Agent
- **Functions**:
  - Create/update projects
  - Manage workflows
  - Email address lookup
  - Bookkeeping integration
- **Integration**: Odoo API

### 7. **Project Execution Supervisor Agent**
- **Purpose**: Task distribution and quality control
- **Functions**:
  - Assign tasks to specialized heads
  - Monitor progress
  - Validate results against brief
  - Report to Account Manager

### 8. **Specialized Execution Agents**

#### 8a. Request Head Agent
- **Workflow**:
  - Set up request
  - Check request
  - Send newsletter
  - Track additions
  - Assess need for additional search
  - Shortlist tracks
  - Check TBC submissions
  - Final shortlist
  - Send to client
  - Monitor engagement

#### 8b. Playlist Head Agent
- **Workflow**:
  - Set up playlist
  - Fill playlist
  - Shortlist
  - Quality check
  - Send to client

#### 8c. Production Head Agent
- **Workflow**:
  - Create mood playlists
  - Create composer reference playlists
  - Fill playlists
  - Shortlist
  - Quality check
  - Send to client
  - Create transfer folders

### 9. **Clearance Head Agent**
- **Purpose**: Manage rights clearance process
- **Workflow**:
  - Research rights holders
  - Estimate payout
  - Draft communications
  - Send emails
  - Negotiate fees
- **Sub-agents**:
  - Fee Estimator
  - Rights Holder Researcher
  - Rights Holder Communicator

### 10. **Account Manager Agent**
- **Purpose**: Client communication hub
- **Functions**:
  - All client correspondence
  - Request missing information
  - Present options
  - Manage expectations
  - Follow up on engagement

### 11. **Support Agents**

#### 11a. Down/Uploader Agent
- **Functions**:
  - Parse emails for file access
  - Download from various platforms (Box, Disco, etc.)
  - Upload to TF platform
  - File management

#### 11b. Transfer/Nextcloud Agent
- **Functions**: Manage file transfers and storage

#### 11c. General Web Searcher Agent
- **Functions**: Perform general research via LLMs

## Key Workflow Principles

### 1. Creative Excellence
- 100% fulfillment of creative expectations (never 90%)
- Look for extra ideas and different approaches
- Understand musical impact potential

### 2. Business Flexibility
- Work within budget constraints
- Propose alternative solutions when needed
- Options: affordable licensing, bespoke production, covers, term changes, fallbacks

### 3. Quality Control
- Multiple checkpoints throughout workflow
- Management oversight for high-value projects
- Engagement monitoring and follow-up

## Implementation Priorities

### Phase 1: Core Infrastructure
1. Email Handler & Brief Extractor
2. Project Strategy Head
3. Basic search agents (Spotify, TF Platform)
4. Account Manager communication

### Phase 2: Search Enhancement
1. Head of Search orchestrator
2. Specialized search agents
3. AIMS integration
4. Chartmetric integration

### Phase 3: Execution Automation
1. Request/Playlist/Production heads
2. Clearance workflow
3. File management agents

### Phase 4: Advanced Features
1. Predictive analytics
2. Automated follow-ups
3. Performance tracking
4. Client preference learning

## Technical Considerations

### Integration Requirements
- Gmail API for email handling
- Spotify Web API
- Chartmetric API (existing)
- Odoo REST API
- Internal TF platform API
- AIMS similarity system
- Various file storage APIs (Box, Nextcloud, etc.)

### Data Management
- Centralized project database
- Track metadata storage
- Client preference profiles
- Rights holder information
- Historical project data

### Security & Compliance
- Secure handling of budget information
- Rights management data protection
- Client confidentiality
- Audit trails for clearances

## Success Metrics
- Time from brief to first presentation
- Search result relevance
- Clearance success rate
- Client satisfaction scores
- Project profitability
- Reuse of previous searches/clearances