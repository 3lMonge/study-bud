# StudyBud Usage Guide

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Launch the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Step-by-Step Walkthrough

### Step 1: Upload Your Study Materials

1. In the sidebar, ensure you're on the **Upload** page
2. Click "Browse files" and select a PDF document (e.g., textbook chapter, lecture notes)
3. Click **"Extract and Store in Vector DB"**
4. Wait for processing to complete
5. You'll see a success message with the number of chunks stored

**Tip**: You can upload multiple PDFs - they'll all be combined in the vector database.

### Step 2: Open the Chat Interface

1. Click **"Open Chat"** in the sidebar
2. You'll see the StudyBud interface with quick action buttons

### Step 3: Start Studying

#### Option A: Get a Study Plan

**What to do:**
- Click the **"📖 Suggest Study Chunk"** button OR
- Type: "What should I study first?"

**What happens:**
- StudyBud analyzes your materials
- Suggests 2-4 key concepts to focus on
- Cites the source document and page numbers

**Example response:**
```
Here's a focused study chunk for you:

📚 Suggested Study Topics:

1. **Photosynthesis Overview** (biology_ch3.pdf, page 1)
   - Definition and importance
   - Overall chemical equation: 6CO2 + 6H2O + light → C6H12O6 + 6O2

2. **Light-Dependent Reactions** (biology_ch3.pdf, page 2)
   - Takes place in thylakoid membranes
   - Produces ATP and NADPH

Review these concepts, then I can quiz you on them!
```

#### Option B: Get Quizzed Immediately

**What to do:**
- Select your difficulty level in the sidebar (easy/medium/hard)
- Click the **"❓ Quiz Me"** button OR
- Type: "Quiz me on photosynthesis" or "Give me a hard question"

**What happens:**
- StudyBud generates a question at your selected difficulty
- Wait for you to answer

**Example interaction:**
```
StudyBud: [Medium] Why does the rate of photosynthesis decrease 
at very high temperatures, even with adequate light and CO2?

You: Because the enzymes denature

StudyBud: Good thinking! You're on the right track...
[detailed feedback explaining correct and missing parts]
```

### Step 4: Review Topics

**What to do:**
- Click **"📋 List Topics"** OR
- Type: "What topics are covered?"

**What happens:**
- Shows all major topics found in your documents
- Organized by source document

### Step 5: Get Summaries

**What to do:**
- Click **"📝 Summarize Materials"** OR
- Type: "Summarize photosynthesis" or "Give me a summary"

**What happens:**
- Provides a concise overview of the topic
- Organized by source document

---

## Study Strategies

### Strategy 1: Systematic Learning
```
1. "List all topics"
2. "Suggest what to study about [topic]"
3. Study the suggested material
4. "Quiz me on [topic]"
5. Answer and get feedback
6. Repeat for next topic
```

### Strategy 2: Progressive Difficulty
```
1. Start with /easy difficulty
2. Get quizzed until comfortable
3. Switch to /medium
4. Master medium questions
5. Challenge yourself with /hard
```

### Strategy 3: Focused Deep Dive
```
1. "Summarize [specific topic]"
2. Read the summary
3. "Suggest study material on [topic]"
4. Study the detailed chunks
5. "Give me a hard question about [topic]"
6. Test your mastery
```

---

## Difficulty Levels Explained

| Level | Question Type | Example |
|-------|--------------|---------|
| **Easy** | Recall, Definition | "What is photosynthesis?" |
| **Medium** | Comprehension, Application | "Why does temperature affect photosynthesis?" |
| **Hard** | Analysis, Synthesis | "Design an experiment to test if blue light is more effective than red light for photosynthesis" |

---

## Advanced Tips

### Conversational Study

You can have natural conversations with StudyBud:

```
You: I'm struggling with genetics

StudyBud: I can help! Let me suggest a focused study chunk on genetics...

You: Actually, can you quiz me on what I already know?

StudyBud: Sure! [Medium] What is the difference between...

You: [your answer]

StudyBud: [detailed feedback]

You: Can you explain Punnett squares more?

StudyBud: [searches materials and explains]
```

### Custom Queries

- "Explain the differences between mitosis and meiosis"
- "What are the key points about DNA structure?"
- "Test my understanding of genetics"
- "I'm confused about crossing over - can you help?"

### Context Awareness

StudyBud remembers your conversation, so you can:
- Follow up on previous topics
- Ask for clarification
- Request related questions
- Build on earlier discussions

---

## Troubleshooting

### "No documents have been uploaded yet"
- Go to Upload page and upload a PDF first

### "ANTHROPIC_API_KEY not found"
- Set the environment variable: `export ANTHROPIC_API_KEY=sk-ant-...`

### Agent returns error
- Check your internet connection
- Verify your API key is valid
- Ensure documents are uploaded

### Questions not relevant to materials
- Upload more comprehensive study materials
- Try being more specific in your queries

---

## Best Practices

✅ **DO:**
- Upload comprehensive study materials
- Start with easier questions and progress
- Read StudyBud's feedback carefully
- Ask follow-up questions when confused
- Use study chunks before quizzing

❌ **DON'T:**
- Upload documents without relevant content
- Skip reading feedback
- Only do easy questions (challenge yourself!)
- Ignore topics you find difficult

---

## Example Study Session

```
[Upload biology textbook chapter on photosynthesis]

You: Hi! What can you help me with?

StudyBud: Hello! I can help you study the materials you've uploaded. 
I see you have content on photosynthesis, cell division, and genetics. 
Would you like me to suggest what to study first?

You: Yes please

StudyBud: [suggests study chunk on photosynthesis basics]

You: Okay, I've read that. Quiz me!

StudyBud: [Medium] Explain why chlorophyll appears green to our eyes.

You: Because it reflects green light

StudyBud: Excellent! You've got the core concept correct. Chlorophyll 
absorbs red and blue wavelengths for photosynthesis and reflects green 
light, which is why we see it as green. You might also mention that 
chlorophyll a and b have slightly different absorption peaks...

You: Give me a harder question

StudyBud: [Hard] The Calvin cycle can continue in the dark using ATP 
and NADPH from the light reactions. However, if a plant is kept in 
darkness for an extended period, the Calvin cycle stops. Explain why...

[Continue studying...]
```

---

Happy Studying! 🎓
