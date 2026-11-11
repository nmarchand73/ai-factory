---
title: "Build a Better Software Factory with Claude Code"
source: "https://www.youtube.com/watch?v=RiaTyJ2POVo"
author:
  - "[[ZazenCodes]]"
published: 2026-11-09
created: 2026-11-11
description: "Get started with Claude Code on the Max plan:► http://clau.de/ZazenCodesEvery developer should build their own software factory. Not just for the leverage that you'll get on your project, but becau"
tags:
  - "clippings"
---
![](https://www.youtube.com/watch?v=RiaTyJ2POVo)

Get started with Claude Code on the Max plan:  
► http://clau.de/ZazenCodes  
  
Every developer should build their own software factory. Not just for the leverage that you'll get on your project, but because it's really cool! This video is sponsored by Anthropic.  
  
AGENTIC CODING CLUB \[ ⚡ become an expert AI builder \]  
► https://www.skool.com/zazencodes-agentic-coding-club-7823  
⚡ Weekly LIVE sessions to ask me questions  
⚡ FULL course access  
  
NEWSLETTER \[ 🍰 get my software factories PDF \]  
► https://zazencodes.com/newsletter  
  
SOFTWARE FACTORY SOURCE CODE \[ ⭐ leave me a star! \]  
► https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code-v2  
  
MY AGENT SKILLS \[ ⭐ /tldr ... and more \]  
► https://github.com/zazencodes/skills  
  
0:47 - Walk Through the Software Factory Mind Map  
4:57 - Install the Factory in a Project  
7:26 - Run the First Issue Through the Factory  
14:30 - Run the Remaining Issues in Parallel  
27:54 - Review Tradeoffs and Next Steps

## Transcript

**0:00** · Today we're building a better software factory with Claude code. Thank you to Anthropic for sponsoring today's video.

**0:06** · In the last video we built a basic software factory that can live inside of your project. People really seem to like this, like a lot. And there was also a lot of great feedback about how I can make that software factory better. So in today's video I did that. It uses GitHub issues, it submits PRs, it does multiple jobs in parallel from a single orchestrator, it uses Fable and Haiku.

**0:30** · And it also has some more deterministic steps so that we're producing higher quality code from our factory. In the hands-on section of the video I'll start by showing you how to install this inside of your own project. I'll be doing that for one of my projects and demonstrating how to use it. I would highly encourage you to follow along with me in that part of the video.

### Walk Through the Software Factory Mind Map

**0:47** · Here's the full mind map from the video and you can get this if you sign up for my email newsletter. I'll send you this image that you can use as reference. The big things going on here is this is the factory. I'm going to explain this soon.

**0:58** · This is the prompt that use to install this in your own project. Here is my previous video on software factories. If you didn't watch that, what I did was I built a modular software factory that can live inside of your project. This is driven by Claude code sub-agents. If you want to learn more about the historical context of software factories, I still recommend watching the start of that video. Otherwise, this video will have everything you need. Here's what's new in V2. We have an intake step which uses Fable. We've got better routing using Haiku agents and this is more dynamic.

**1:29** · We have more determinism built in so that we're doing more tests throughout the pipeline so that our software factory is more reliable. It runs on GitHub issues. This is the input and the output is a PR that gets pushed to our GitHub project. And we have better observability and cost and time per job and stuff like that. So to really understand that, let's look at the factory flow diagram. The input to our factory is a GitHub issue or multiple.

**1:54** · It can take in many GitHub issues at once and process them all together. And these come into an intake step, which is Fable. This is a new step in this version of the factory where Fable thinks about if this is worth building.

**2:07** · It scopes it out within the context of the project. It assesses it for risk, and it could potentially reject the feature or ask for more information from a human. Next, we're going into the spec writing and building step, and these are still two distinct steps, but I'll talk about in my closing thoughts for the video how these could probably be merged into a single step. From here, we're going to push our code through a gate.

**2:29** · This is a new deterministic step, and the idea here is that we're really wanting to validate that the software factory is correct. And so, this is a cheap step where we can run this on the build and make sure it's looking good.

**2:40** · And if it's not, we can go back to the builder, and then eventually, when we get through the gate, then we go to some reviewers. And so, we're going to do a code review, and this will be done with Haiku or Sonnet if it's deemed risky.

**2:52** · And the risk comes back to this assessment which was made by Fable at the start of the pipeline. And I did this because I wanted to demonstrate how we can use agents inside of our software factory to inform later steps and to potentially cost optimize our software factory. Uh we're also going to go to other reviewers, and we'll do this all in parallel, and depending on the results of these, we can push the job back to the builder to fix.

**3:13** · And once we get through the code review, then we go to an approver step, which decides if this can be merged automatically or if this needs human review in order to close out the loop on our software factory and implement this feature into the codebase. Now, having seen this factory flowchart, there's a whole section of stuff over here, but I want to get to this later in the video. This is more details around the how the system works. Right now, I want to focus on this, which is how to actually use this system with Claud code.

**3:41** · We start with an orchestrator, and the orchestrator is a Claud code session that I'm going to spin up, and inside of that session, I'm going to say factory run. From here, it will start spinning sub agents, background agents in Claud code that will be doing various tasks within our system. It also has a deterministic spine, and what this means is I have actual scripts, like checks.sh, this gate script, this route script. I have a jobs script. These are shell commands that are shipped with the factory.

**4:10** · I'll show you these later in the video, and these are doing deterministic things to push our jobs through the the pipeline, through the actual factory. So, we have these commands: factory run, factory run n, where n is a number, like a specific GitHub issue that we want to process.

**4:27** · And we can just pass anything we want in here. We can just pass any arbitrary string in order to do stuff within our factory context inside of our project.

**4:36** · And this all comes with the skill that I'm going to show you how to install in the video. Another thing that comes along with this is a dashboard so that we can view everything as it moves through the factory. And the other important things to know are that we have concurrency built in here. So, we'll process up to three jobs at once, and this is a configuration setting, which you can change after you've installed the factory in your project.

### Install the Factory in a Project

**4:57** · So, let's get started by installing the factory. So, this is the prompt that you can copy and paste into your own project in order to follow along with me in the demo. So, I'm just going to copy this, and I'm going to go over to my terminal.

**5:08** · And I'm inside of a project called note wall app. Just a simple note application. I can sort of write stuff.

**5:15** · That's it. I've also got this app on GitHub, and this is important for the issues and the pull requests, which will be a core component of our software factory. So, I'm going to spin up Claude Code, and we'll use Claude to install our software factory. And I'm just going to paste this in. So, it says, "Install this software factory in this project, and this is the reference repository."

**5:34** · It's a link to my source code for this video. And here's that exact link. If you open it up, you'll see something like this, and you'll see that prompt is actually right in here in the source code. So, you can get this in the video description and find this link. You'll notice that we have this folder .claud.

**5:48** · We also have this factory folder. Both of these are going to appear inside of your project after this is installed.

**5:54** · Let me go ahead and run this.

**5:56** · This just finished up, and let me show you what was installed. So, if I go into note wall app and look at this inside of Vim, the two main things we've added are this .claud folder, and inside of here I have a bunch of agents files. These are the sub agents, the descriptions of how our sub agents in the factory work. And we've got skills and inside of skills I've got one new skill installed which is factory and it has one file called skill dot MD which describes the entire behavior of the factory. But that's not all of the code that you just got.

**6:23** · You also got this folder which is called factory and here's where we have all of the code dependency for the factory. The big things to pay attention to are the bin files. These are what are responsible for ingesting and pushing things through the factory as jobs. We have check dot SH which does deterministic checks like classic CICD stuff as stuff gets pushed through our factory. We have a configuration file where we can specify behavior of our factory and we have a dashboard file basically observe our factory. Now coming back up I want to show you this.

**6:55** · So there's a bunch of stuff Claude says changed for NoteWall and there's a whole bunch of stuff of how the software factory that I provide the template was actually adapted to your project. And the big things are this one. Check dot SH is going to run your actual tests inside of your project. This line right here agents dot MD has a new software factory sections and let's look at that new section that was added. It looks like this. Software factory. So we're explicitly documenting how to use the software factory inside of our agents file.

**7:24** · Now let's get out of this and I'm going to start a new session up here with Claude and I want to actually demonstrate our software factory in use.

### Run the First Issue Through the Factory

**7:31** · Now I'm on Opus 5.5 with low effort. And let's see what happens if I just try and run the factory right now. I'm going to say factory run. And we're checking.

**7:40** · Factory bin job queue. We are running a script inside of our factory to see what's in the queue. And it says oh, it came back empty. There's nothing going on. So let's go over to GitHub and put something in our queue for the factory and you can see that I have a bunch of open issues. However, these don't have the right label on them. So they're not going to get picked up by the factory until we explicitly label them.

**8:00** · This is just a safety measure that I shipped with the factory because the idea is many bit different people might be adding issues into your project, but you want to choose which ones get processed by your factory. Let's pick up just one issue to start with. I've got this one called dark mode, and I'm going to go to labels, and I'm going to add the factory label. If you don't see this, you can just create it. It won't exist for your project unless you create it yourself.

**8:25** · And now that I've done that, I can see this label's been applied. So, I can go back to my factory, and if I run the exact same command again, now it'll pick that up and start processing it through the factory. And we can see it's creating a job, and it is in the intake stage now for this dark mode feature.

**8:43** · That is now serving. So, we can see issue one, dark mode, is in the intake step. This is being processed by Fable, and I wanted Fable to do the first step of our factory because to me, that's just a really important step to understand what's happening in the context of our project. Next, we've moved into the spec writer. So, I can show you that if I click into this, we can get more information. We're going to see a bunch of different files being accumulated as the task gets pushed through the factory. We just saw spec got created, and this is what was created by the spec writer.

**9:14** · But before that, we had Fable write this intake form, and Fable decided to accept it, and it decided it was low risk. It only touches the UI as a surface, and it has a little summary of all the sort of big things you'd want to know, and then a full agent log of like more information that Fable was thinking around this feature. And this is really important in a factory to understand what the agent was thinking as it pushed your thing through the factory. It's really important for debugging and analyzing the effectiveness of the factory over time just to keep all of this information around from your job.

**9:45** · So, now we're in the builder phase. Let me come back to Claude, and let's see what's going on over here. I can actually see the builder as an agent down here, and this is a sub agent in Claude code. And what I can do is click enter and go into that. So, I can actually see what this sub agent is thinking, and I could steer it. What are you doing? Now, this level of interaction with the agent is kind of not really the point of the software factory. I'm going to talk more about that in my closing thoughts, but I just wanted to show you how you can do this with Cloud Code. Let's go back to the main agent.

**10:15** · So, this is going to be our orchestrator, and in principle, this could spin up other jobs at the same time. Now, let's follow this one task all the way through. The build just finished, and we're seeing that now it's in the review phase. And this means that it passed the gate. The gate was this deterministic step that we had to go through, where we're running certain tests and linting and stuff like that.

**10:36** · And I can show you that go back to Obsidian. This is the part that we just got through. So, we just went through the gate, and we're getting a green check mark on that. And now we're going through all of these guys. So, coming back to our terminal, and bringing this back up, we can see that's why the gate went green here.

**10:53** · Now, we see the UX guy just approved, so this is done. We're just waiting on the code review and the UI review. And then we'll go through the rest of the pipeline. But, look at this, the code review just failed. We got orange for the code review. That means we're going to get kicked back to the builder phase.

**11:10** · And let me just quickly show you that.

**11:12** · So, now we're going to follow this route, and we're going to have to go back to the builder with some feedback, and then we'll have to get pushed through again. So, we're actually seeing this self-fixing recursive aspect of the pipeline now. And we can look at that.

**11:25** · We can look at more information. So, let me come in here, and I'm going to click on the code, and the verdict was one readability gap. This reviewer was basically really being really picky about something, and it kicked it back because like how something was working.

**11:39** · Now, notice how the code review is using haiku or only saw on it if it's determined to be risky. I'm going to come back to this later because it turns out that using models like haiku in this phase of the pipeline might not be such a good idea. These models aren't always able to understand the code as well as the builder. So, it can create an actually bad dynamic when you have code review happening by an agent that's not as intelligent as the builder agent. In any case, coming back here, we see that the UI has also failed.

**12:08** · And so, now Now kicked back, and we're going to go through another round of reviews after we build pass our gate. We're going to have to get these guys to review it again based on the feedback that they've provided to the builder. And here they go. They're back into the next round of review. We can see this time the code is going green and hopefully the UI agent passes as well. Nice. It went green and we are in the approved phase. Now this approver is going to decide if it's can be automatically merged or if it needs human review before it merges.

**12:37** · And I think this is a cool thing that our factory can do because it can allow for a lot more autonomous behavior. If it's a straightforward feature that can be merged without us looking, that saves human time. That's valuable and that's something I want my factory doing for me. And indeed it's done. So we can see we have a PR that was created for this and it's been merged. So this has actually been merged into our production code. Let me show you that over on GitHub. Here it is. It's called dark mode one. This was from the intake step.

**13:07** · We actually just wrote some stuff in here 6 minutes ago. I opened a pull request and then I marked it as completed. So let me go to the PR. This is the one associated with that issue and I added a bunch of stuff. This is all the commits that our software factory was making and then down here we're saying pull request successfully merged and closed. Our system decided it didn't need my attention. It's something that could be automatically merged but we have the full history of how this worked inside of GitHub which I think is very powerful for observability. And if I go to the code, I can see that I merged a pull request.

**13:36** · This was done a minute ago and that's now in the code base. Now let's pull these changes in from the remote. So if I say get status, I should see some files that have changed locally. And what we're seeing here are the files and folders that were added or modified when we installed the software factory itself. I never added and committed these. So let me do that now. All right. Adds as in code software factory and these are all the files that we were looking at earlier. You'll also notice that I'm on main right now. So I'm working on my main branch and now I'm going to pull in the remote changes from main. I'll just say get pull.

**14:08** · I'm going to have to clean up some merges but okay, we did auto merging. So it's all good. There were some conflicts with the agents, but we handled it. So, now we pulled these changes in and you can see a bunch of changes to stuff like the style and the theme. This is for our dark mode feature. Now, let me show you that. I'll say npm run dev and let me show you this app again. So, here it is.

**14:27** · Now, I have a dark mode going on by default. It's dark now. Okay. So, now that I've showed you how to take one issue and push it through our entire factory, I want to show you how to do this for many issues at once. Now, I've got four issues open in here. I'm going to grab all of them and I'm going to add the factory label to all of them at the same time. And now, all of these guys have the factory label. So, let me come back to Claude and we're going to process everything at once. Now, let me just come back here. If I run factory run, it's going to process everything together.

### Run the Remaining Issues in Parallel

**14:56** · But, I could also say factory run and then just give a single number and just process that issue. I want to demonstrate that right now. So, I'll just say factory run and let's just pick one issue. Issue number four is called different fonts. So, let me just say four. It's looking at the queue and that's reading all of these from GitHub and it's found the right one in take issue number four, different fonts. And now, it's processing that through our factory. I can check in on that and here it is. Different fonts is now in the intake step. So, Fables having a look at that. Now, let's process the rest.

**15:27** · And because this session right here is the orchestrator, I can keep continuing using it and I can use this orchestrator to interact with existing jobs in our factory or I can use it to create new jobs. And that's what I want to do now.

**15:41** · So, I'll just say factory run and this is going to process everything else.

**15:46** · It's going to pull all of the issues and push them through our factory and we're going to see these all starting to appear in the intake step. There they are. Notice how we just have three things running. This is because we set our concurrency for our factory to three. What's the uh concurrency setting? Currency is three in factory.config.json.

**16:04** · Now, let me show you some other new stuff that's in our factory. We're timing these jobs. So, I can see this dark mode job has a time of 8 minutes.

**16:13** · That's how long it took to push through the whole factory. We're also providing a cost. So, this one says $3.40. It didn't actually cost me $3.40 to push this through the factory. It was free for me. I just used my Claude plan.

**16:25** · However, this gives us an idea of how expensive these jobs are when benchmarked against each other, and then we can use that to try and optimize our factory. We can try and make this more efficient by looking at the job cost and trying to push this down in certain ways. So, I thought that was an important addition to this factory. Now, let's look at what's going on. We have a job that's in the needs human. So, this thing is effectively unpaused. And because of that, we've now automatically started the intake for the final issue.

**16:52** · This is called multiple walls. Now, let's focus on this step that needs human review. There's two ways that we can do this in our application. The first way is I could actually click on it, and now I can start to sort of look at it and examine these files which are being written durably to our factory.

**17:08** · So, I can see that the build has been blocked, and there's this decision.md why the builder was blocked. This is not how I would inter- interface with the factory. I would just talk to Claude up here. This guy is the orchestrator. He's managing everything, but his chat is fairly free for me to talk to. Or what I could do is spin up a new Claude code instance inside the same project. And as long as I use the factory skill, I can just ask whatever I want. What happened with the different fonts task? I can see this needs a decision for me. What happened? Intake accepted the issue with a narrower scope. It doesn't really know what to do for font.

**17:39** · Default to handwriting. It wants some input from me. Now, because this is a video and I don't really care, yeah, just do whatever you want. Let's get this going again. So, that should be able to push this task back along. I've basically made my decision, and now our software factory should pick this up, and you can see we've just added this feedback one.md. I can click in there, and it says, "Yeah, just do whatever you want.

**18:01** · Let's get this going again." And now we'll see this job go somewhere, and here it is. It's back in the building phase. Meanwhile, our colored sticky notes is just waiting on the UI, and then this should This one should be built out, and the multiple walls has been called high. So, this is like a high-risk feature, and that's a label that Fable put on our features. These little labels are things that I added from the initial intake step. I'm getting Fable to decide and based on that information, it adapts the factory behavior as we push the job through.

**18:30** · Check this out. For changing the display name, it has code, it has UX and UI, but there's no security reviewer on that.

**18:37** · Whereas this guy does have a security reviewer and the reason was because this was a medium difficulty. Therefore, it was assigned a security review step.

**18:46** · Whereas this guy was low, so he was not assigned a security review step. This is just a behavior because I wanted to illustrate how we can change and make our software factory dynamic.

**18:57** · Effectively, a dynamic directed acyclic graph. And this can help with efficiencies of your factory. Again, I'll speak more about efficiencies and my thinking around that in my closing thoughts in the video. Now, let me clean up what's going on up here. I've got two Claude sessions going on. This guy on the right, I just used to interact with our factory, but I'm fine to spin that one down. I could just totally get rid of that. Nothing changes in our factory.

**19:21** · But, if I was to try and kill this session, well, this has a bunch of sub agents associated with it. We also have a shell and this shell is the thing that's actually serving our dashboard.

**19:30** · There's no reason Claude has to do that.

**19:32** · I could have served it myself manually, but if I try and spin this guy down, see, I just pressed control C and actually all background agents stopped.

**19:40** · So, all of these guys have now been just totally halted. That's not good. So, what I'm going to say is factory run.

**19:48** · And what this should do is look at the current state. It's looking at the queue. So, it went back to GitHub. It's like, what's going on? It looks at the queue and now it should spin all these guys back up. So, in that sense, the factory is fairly durable.

**20:01** · Now, I'm sure I just lost a little bit of work because whatever those sub agents were doing, we've now spun up new sub agents and you can see these guys all just started from scratch. So, any work that was currently in flight just got completely annihilated and we're we're restarting that. So, in particular, this UI step was currently ongoing and that got blown up and we restarted it. It's not a good idea to do that, but um the factory is pretty durable, right? I just showed you how we stopped it and we were able to spin it back up and now things are getting pushed through. And now I can see everything's accumulated here.

**20:30** · It either needs review and then there's two that have finished. And looking at this in GitHub, now I can see we've got flag from our software factory on three issues. And if I go to the pull request, three open PRs for each of these and there's two closed ones. And in the source code itself, of course, we're going to see that that was pulled in.

**20:49** · Merge pull request number seven, change display name. Now, coming back to our factory, and I just love this idea that we can come back to it with a very totally clean project and just run this factory command in order to get all the context from inside of here. What's going on with the different fonts? We need a call on this.

**21:07** · So, let's see. The fonts is stuck in the factory rule, not the feature. It needs a call from you. All right, so this guy here, different fonts, this was blocked because of an issue with my software factory. So, I just fixed the factory. I told it hey, go fix yourself. This should have never been blocked. We should have been able to keep building this. When I wrote it up here, I just want to be real with you guys. I was like, also update V2 factory in Zazon code season 3. So, that means the factory you install will have this fix.

**21:35** · Like, this should be fixed for you. So, this has got picked up and now it's getting tossed back to the builder phase. So, we will work through that one. Now, let's talk about the other ones. Now, since I've already loaded my factory, I'm just going to ask questions directly. How about issue number five?

**21:48** · What's going on there? All right, now there's some noise going on because this other job's running, but this is what it said. There's a lot of stuff in here.

**21:54** · I've got this skill. This is just my own skill. It's called TLDR. So, what my TLDR skill does is it just shortens the output of the agent. Okay, I trust you to handle this one properly. You can do that. Next, what's going on with issue number three, the colored sticky notes?

**22:09** · The new color tester never runs because it skips server. May I send it back with move test and run color. Do that. Sounds good for issue number three. Now, these guys here appear to be needing human review, but I've already kicked these along. So, if I refresh this, I can see this one's actually changed. It's getting built now. The multiple walls is still here. What should we do about the multiple walls issue number five? Okay, so for issue number five, we're actually intentionally made it. We're waiting.

**22:37** · We're waiting for these other tasks to finish. The orchestrator has some sort of shared understanding, right, of what's going on in the system and we're waiting on this until these guys have finished and then we're going to merge this PR in.

**22:49** · That makes sense to me. And notice how we keep getting these TLDRs. That's from my skill, so I could just say this and I'll say, "Stop outputting TLDR." I'll leave a link to this and my other ones in the video description. If you like them, please leave me a star. Helps me out a lot on this channel and with my brand. And if you're enjoying this video on software factories, you can get my PDF guide if you sign up for my newsletter. This just has a structured summary of what we talked about in this video, along with links and installation commands. You can send this to your friends or use it yourself. This is my newsletter. I just send one email a week.

**23:21** · And if you sign up for this, I'll also give you some other stuffs like my agentic engineer playbook. This just has my like philosophy on agentic engineering and basically this new age that we're going into as software engineers. Now, everything's done except for this last multiple wall. And what's going on with multiple walls? I'm going to get TLDR working on that. It's stalled. It waits on your sign-off for the wall format.

**23:46** · One round to merge.

**23:48** · Yep, let's do whatever you want and merge it in. We also have links here. I can click this link and open up the PR directly. Okay, I think it's worried about throwing out some data. This is just a test app, I don't care. Yeah, just get rid of the data right now. Just test data, it doesn't matter. I love this one. I love how it's like actually recording these. So, we have factory bin job feedback. This is a function in our factory that explicitly sets feedback from the user and we have tons of these functions. I want to show you these in in just a minute. We're about to get to this. Let me just show you the final version of the application.

**24:18** · So, I'll pull all the changes in. So, here's our our thing. We can now change the color of the sticky notes. That's cool. This one will be red. Let's go with red.

**24:31** · Yeah, nice. Okay. And there was also Oh, I can change my name. Okay, cool. Now, if I do new one, I'm talk now.

**24:40** · Yeah, there he is. Okay. Go back to our mind map and sort of walk through these.

**24:45** · So, the deterministic checks are handled by this checks.sh.

**24:49** · This is something that checks and deterministically fails if we're not meeting the right things that we need in our project. If we're not passing the tests, and it's very simple. Look at this. It's a bash file, and it's going to run through, and it's going to run all these npm commands because we have an npm project. But if you have a different project, you'll be running different tests in here. So, we're doing a linting, we're doing a type check, we're doing npm test, and then we're running a build. We're actually building our project, making sure all of this works. If If something goes wrong here, we do not even get to the reviewers.

**25:20** · It hasn't even made it that far because this gate is put in place right in front of them. So, job.json drives all of the stages. This is a file that's on your computer that lives and represents the job as it gets pushed through the factory. And this thing is only written It's only updated by factory bin job. This is not like a vibey thing that gets updated by Claude code. Claude code calls factory bin job in order to update this JSON file. And let me show you that.

**25:50** · It'll be very obvious when you look at this. Let me look at job inside of here. And it says right at the top, "The only writer of factory jobs job ID job.json." We have all these different commands like job queue. This looks at the queue of what's going on. If I follow queue, we can kind of see probably This might be a bit messy, but we're going to be looking at GitHub. Do you see issues equals gh.json? This is looking at GitHub and seeing what's going on inside of GitHub. So, then there's job create, job advance, job merge.

**26:21** · And this is what's responsible for pushing things through our pipeline, running this script. Let me show you the actual jobs. Now, we're not going to see those inside of here because they're being get ignored. If I go into factory and look at everything in here, we have a jobs folder. This is where the actual data of the stuff in our factory lives.

**26:40** · You should know that this data just lives on your computer. This is being get ignored. It's not being got backed up to GitHub. So, if you wanted to persist this, you could build something in in order to persist this separately, and that's what I would do. I would build in something that saves this data to Google Cloud Storage, and I would just say, "Hey Claude, I want to save this stuff to Cloud Storage. Let's set up a workflow for doing that. It'll handle that for you." This is the data that we keep seeing in our factory, including round one, round two, round three. This is the data that if I look inside of here is populating all of these files right here.

**27:09** · Um it's just coming from those markdown files that's on that's on my actual system. And I've got this job.json. So, this guy right here, this is the file that is being edited by those bin scripts. When it says only factory bin job writes it, this is the thing that is making our software factory durable and properly passing jobs through the life cycle of the factory. The big point is that this thing is worked on programmatically.

**27:35** · Claude does not work on this itself.

**27:38** · Claude runs functions in order to update this file. Hope that's clear. That's really important for how our factory is working. Right, we've pretty much covered everything. Thank you to Anthropic for sponsoring today's video.

**27:49** · And if you're not using Claude Code yet, then you can click the link in the video description and sign up now. Let me share some closing thoughts on what we've built today and where I want to take this next. First of all, this is definitely an improvement on my software factory from the previous video. There's a lot of things that I thought through better, and I like how this one is working better than that previous one.

### Review Tradeoffs and Next Steps

**28:09** · However, it's also more complicated. And with complexity doesn't always come improvement. So, I would encourage you to look at this factory and say, "How could I actually simplify this a little bit for myself while still getting all the performance that that I want out of the factory?" Next thing I want to talk through is cost. So, we're tracking the cost or like the estimated cost if we were paying token prices. Again, we're not paying token prices, so that's something to keep in mind, but it's still a good benchmark that we can use to try and optimize the cost over time and compare the cost of different jobs.

**28:39** · And what we might want to try and do is use cheaper models like Haiku at certain places in the pipeline. For example, maybe we could use Haiku in the reviewer phases. However, if we're doing this and now the reviewers are failing because they're using Haiku and they're just not really thinking very intelligently about the problem and then they're kicking work back to the builder, that could actually end us end up costing us more money. So, that's something I would I would be careful about doing. Um potentially the approver could be a Haiku agent.

**29:06** · But, then as well, we're like, do we want to put the choice of approving this feature into our code base on Haiku? I don't know if I want to do that. And I really like how we're using GitHub issues and pull requests.

**29:19** · And something cool that we could do would be to watch the performance metrics of our actual production system and then be pushing those things automatically into GitHub issues where they could then be ingested into the factory. So, if we wanted to basically bring in a layer of, you know, post-implementation monitoring, like post-production uh deployment monitoring in our actual system, we could do that through this exact factory, through the GitHub issues, like form factor.

**29:43** · We can be getting other systems, any other system we have, to be pushing GitHub issues into our project, adding the factory label, and then it gets picked up here and pushed through our system.

**29:56** · So, we don't actually need like extra layers in order to attach things like observability. That's pretty much already handled for us by the GitHub issues. Okay, the last thing I want to talk about is actually using this in production. So, this is the big complaint with software factories. It's like, okay, yeah, that's cool, but you'd be a a psycho to actually plug this into your real production system.

**30:17** · And I would have to agree with you, right? This is a 30-minute video that you've watched about how software factories work, how you can build one for yourself. I'm not telling you that you should take the code that I've showed you in today and plug it into your production system and close your eyes and get your agents chugging through all of your all of your issues for you and building your application in in that \[music\] way. Um I do think it's something you could do in the way that I showed you how we're controlling it and we're sort of looking at it and we're checking how it goes. Yeah, sure. That's a that's a thing you could do.

**30:49** · I think this is a thing you could start with and I think that actually software development in general will go to an abstraction layer that looks like this.

**30:59** · That's less about coding agent harnesses like we're seeing them today like Claude um how Claude code works today but instead from a higher level like super Claude code where you're you're sort of managing above the agent harness level in the same type of way as we're seeing this video. So I think the concept of a software factory is very important to understand. I think what I'm showing you today could be the basis of something that would work in a production system um and I think that you just have to be very thoughtful about actually how that should should happen for you.

**31:26** · Um and I and I'd love to hear your thoughts on that as well. So what's next for me with my software factory? Well, I'd love to hear in the comments ways that we you think this can be improved or modified but the big thing I'm thinking is how do we get this running in the cloud? Like I don't want to run this on my computer anymore. I want this just automatically running somewhere and I think the Claude agent SDK would be the way to go for this. So that's what I'm considering for my next video. Love to hear your thoughts on that and thank you for watching.