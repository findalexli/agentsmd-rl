#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "description: \"When the user needs marketing ideas, inspiration, or strategies fo" "skills/marketing-ideas/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/marketing-ideas/SKILL.md b/skills/marketing-ideas/SKILL.md
@@ -1,11 +1,11 @@
 ---
 name: marketing-ideas
-description: "When the user needs marketing ideas, inspiration, or strategies for their SaaS or software product. Also use when the user asks for 'marketing ideas,' 'growth ideas,' 'how to market,' 'marketing strategies,' 'marketing tactics,' 'ways to promote,' or 'ideas to grow.' This skill provides 140 proven marketing approaches organized by category."
+description: "When the user needs marketing ideas, inspiration, or strategies for their SaaS or software product. Also use when the user asks for 'marketing ideas,' 'growth ideas,' 'how to market,' 'marketing strategies,' 'marketing tactics,' 'ways to promote,' or 'ideas to grow.' This skill provides 139 proven marketing approaches organized by category."
 ---
 
 # Marketing Ideas for SaaS
 
-You are a marketing strategist with a library of 140 proven marketing ideas. Your goal is to help users find the right marketing strategies for their specific situation, stage, and resources.
+You are a marketing strategist with a library of 139 proven marketing ideas. Your goal is to help users find the right marketing strategies for their specific situation, stage, and resources.
 
 ## How to Use This Skill
 
@@ -20,493 +20,493 @@ When asked for marketing ideas:
 
 ---
 
-## The 140 Marketing Ideas
+## The 139 Marketing Ideas
 
 Organized by category for easy reference.
 
 ---
 
 ## Content & SEO
 
-### 3. Easy Keyword Ranking
+### 1. Easy Keyword Ranking
 Target low-competition keywords where you can rank quickly. Find terms competitors overlook—niche variations, long-tail queries, emerging topics. Build authority in micro-niches before expanding.
 
-### 7. SEO Audit
+### 2. SEO Audit
 Conduct comprehensive technical SEO audits of your own site and share findings publicly. Document fixes and improvements to build authority while improving your rankings.
 
-### 39. Glossary Marketing
+### 3. Glossary Marketing
 Create comprehensive glossaries defining industry terms. Each term becomes an SEO-optimized page targeting "what is X" searches, building topical authority while capturing top-of-funnel traffic.
 
-### 40. Programmatic SEO
+### 4. Programmatic SEO
 Build template-driven pages at scale targeting keyword patterns. Location pages, comparison pages, integration pages—any pattern with search volume can become a scalable content engine.
 
-### 41. Content Repurposing
+### 5. Content Repurposing
 Transform one piece of content into multiple formats. Blog post becomes Twitter thread, YouTube video, podcast episode, infographic. Maximize ROI on content creation.
 
-### 56. Proprietary Data Content
+### 6. Proprietary Data Content
 Leverage unique data from your product to create original research and reports. Data competitors can't replicate creates linkable, quotable assets.
 
-### 67. Internal Linking
+### 7. Internal Linking
 Strategic internal linking distributes authority and improves crawlability. Build topical clusters connecting related content to strengthen overall SEO performance.
 
-### 73. Content Refreshing
+### 8. Content Refreshing
 Regularly update existing content with fresh data, examples, and insights. Refreshed content often outperforms new content and protects existing rankings.
 
-### 74. Knowledge Base SEO
+### 9. Knowledge Base SEO
 Optimize help documentation for search. Support articles targeting problem-solution queries capture users actively seeking solutions.
 
-### 137. Parasite SEO
+### 10. Parasite SEO
 Publish content on high-authority platforms (Medium, LinkedIn, Substack) that rank faster than your own domain. Funnel that traffic back to your product.
 
 ---
 
 ## Competitor & Comparison
 
-### 2. Competitor Comparison Pages
+### 11. Competitor Comparison Pages
 Create detailed comparison pages positioning your product against competitors. "[Your Product] vs [Competitor]" and "[Competitor] alternatives" pages capture high-intent searchers.
 
-### 4. Marketing Jiu-Jitsu
+### 12. Marketing Jiu-Jitsu
 Turn competitor weaknesses into your strengths. When competitors raise prices, launch affordability campaigns. When they have outages, emphasize your reliability.
 
-### 38. Competitive Ad Research
+### 13. Competitive Ad Research
 Study competitor advertising through tools like SpyFu or Facebook Ad Library. Learn what messaging resonates, then improve on their approach.
 
 ---
 
 ## Free Tools & Engineering
 
-### 5. Side Projects as Marketing
+### 14. Side Projects as Marketing
 Build small, useful tools related to your main product. Side projects attract users who may later convert, generate backlinks, and showcase your capabilities.
 
-### 30. Engineering as Marketing
+### 15. Engineering as Marketing
 Build free tools that solve real problems for your target audience. Calculators, analyzers, generators—useful utilities that naturally lead to your paid product.
 
-### 31. Importers as Marketing
+### 16. Importers as Marketing
 Build import tools for competitor data. "Import from [Competitor]" reduces switching friction while capturing users actively looking to leave.
 
-### 92. Quiz Marketing
+### 17. Quiz Marketing
 Create interactive quizzes that engage users while qualifying leads. Personality quizzes, assessments, and diagnostic tools generate shares and capture emails.
 
-### 93. Calculator Marketing
+### 18. Calculator Marketing
 Build calculators solving real problems—ROI calculators, pricing estimators, savings tools. Calculators attract links, rank well, and demonstrate value.
 
-### 94. Chrome Extensions
+### 19. Chrome Extensions
 Create browser extensions providing standalone value. Chrome Web Store becomes another distribution channel while keeping your brand in daily view.
 
-### 110. Microsites
+### 20. Microsites
 Build focused microsites for specific campaigns, products, or audiences. Dedicated domains can rank faster and allow bolder positioning.
 
-### 117. Scanners
+### 21. Scanners
 Build free scanning tools that audit or analyze something for users. Website scanners, security checkers, performance analyzers—provide value while showcasing expertise.
 
-### 122. Public APIs
+### 22. Public APIs
 Open APIs enable developers to build on your platform, creating an ecosystem that attracts users and increases switching costs.
 
 ---
 
 ## Paid Advertising
 
-### 18. Podcast Advertising
+### 23. Podcast Advertising
 Sponsor relevant podcasts to reach engaged audiences. Host-read ads perform especially well due to built-in trust.
 
-### 48. Pre-targeting Ads
+### 24. Pre-targeting Ads
 Show awareness ads before launching direct response campaigns. Warm audiences convert better than cold ones.
 
-### 55. Facebook Ads
+### 25. Facebook Ads
 Meta's detailed targeting reaches specific audiences. Test creative variations and leverage retargeting for users who've shown interest.
 
-### 57. Instagram Ads
+### 26. Instagram Ads
 Visual-first advertising for products with strong imagery. Stories and Reels ads capture attention in native formats.
 
-### 60. Twitter Ads
+### 27. Twitter Ads
 Reach engaged professionals discussing industry topics. Promoted tweets and follower campaigns build visibility.
 
-### 62. LinkedIn Ads
+### 28. LinkedIn Ads
 Target by job title, company size, and industry. Premium CPMs justified by B2B purchase intent.
 
-### 64. Reddit Ads
+### 29. Reddit Ads
 Reach passionate communities with authentic messaging. Reddit users detect inauthentic ads quickly—transparency wins.
 
-### 66. Quora Ads
+### 30. Quora Ads
 Target users actively asking questions your product answers. Intent-rich environment for educational ads.
 
-### 68. Google Ads
+### 31. Google Ads
 Capture high-intent search queries. Brand terms protect your name; competitor terms capture switchers; category terms reach researchers.
 
-### 70. YouTube Ads
+### 32. YouTube Ads
 Video ads with detailed targeting. Pre-roll and discovery ads reach users consuming related content.
 
-### 72. Cross-Platform Retargeting
+### 33. Cross-Platform Retargeting
 Follow users across platforms with consistent messaging. Retargeting converts window shoppers into buyers.
 
-### 129. Click-to-Messenger Ads
+### 34. Click-to-Messenger Ads
 Ads that open direct conversations rather than landing pages. Higher engagement through immediate dialogue.
 
 ---
 
 ## Social Media & Community
 
-### 42. Community Marketing
+### 35. Community Marketing
 Build and nurture communities around your product or industry. Slack groups, Discord servers, Facebook groups, or forums create loyal advocates.
 
-### 43. Quora Marketing
+### 36. Quora Marketing
 Answer relevant questions with genuine expertise. Include product mentions where naturally appropriate.
 
-### 76. Reddit Keyword Research
+### 37. Reddit Keyword Research
 Mine Reddit for real language your audience uses. Discover pain points, objections, and desires expressed naturally.
 
-### 82. Reddit Marketing
+### 38. Reddit Marketing
 Participate authentically in relevant subreddits. Provide value first; promotional content fails without established credibility.
 
-### 105. LinkedIn Audience
+### 39. LinkedIn Audience
 Build personal brands on LinkedIn for B2B reach. Thought leadership content builds authority and drives inbound interest.
 
-### 106. Instagram Audience
+### 40. Instagram Audience
 Visual storytelling for products with strong aesthetics. Behind-the-scenes, user stories, and product showcases build following.
 
-### 107. X Audience
+### 41. X Audience
 Build presence on X/Twitter through consistent value. Threads, insights, and engagement grow followings that convert.
 
-### 130. Short Form Video
+### 42. Short Form Video
 TikTok, Reels, and Shorts reach new audiences with snackable content. Educational and entertaining short videos spread organically.
 
-### 138. Engagement Pods
+### 43. Engagement Pods
 Coordinate with peers to boost each other's content engagement. Early engagement signals help content reach wider audiences.
 
-### 139. Comment Marketing
+### 44. Comment Marketing
 Thoughtful comments on relevant content build visibility. Add value to discussions where your target audience pays attention.
 
 ---
 
 ## Email Marketing
 
-### 17. Mistake Email Marketing
+### 45. Mistake Email Marketing
 Send "oops" emails when something genuinely goes wrong. Authenticity and transparency often generate higher engagement than polished campaigns.
 
-### 25. Reactivation Emails
+### 46. Reactivation Emails
 Win back churned or inactive users with targeted campaigns. Remind them of value, share what's new, offer incentives.
 
-### 28. Founder Welcome Email
+### 47. Founder Welcome Email
 Personal welcome emails from founders create connection. Share your story, ask about their goals, start relationships.
 
-### 36. Dynamic Email Capture
+### 48. Dynamic Email Capture
 Smart email capture that adapts to user behavior. Exit intent, scroll depth, time on page—trigger popups at the right moment.
 
-### 79. Monthly Newsletters
+### 49. Monthly Newsletters
 Consistent newsletters keep your brand top-of-mind. Curate industry news, share insights, highlight product updates.
 
-### 80. Inbox Placement
+### 50. Inbox Placement
 Technical email optimization for deliverability. Authentication, list hygiene, and engagement signals determine whether emails arrive.
 
-### 113. Onboarding Emails
+### 51. Onboarding Emails
 Guide new users to activation with targeted email sequences. Behavior-triggered emails outperform time-based schedules.
 
-### 115. Win-back Emails
+### 52. Win-back Emails
 Re-engage churned users with compelling reasons to return. New features, improvements, or offers reignite interest.
 
-### 116. Trial Reactivation
+### 53. Trial Reactivation
 Expired trials aren't lost causes. Targeted campaigns highlighting new value can recover abandoned trials.
 
 ---
 
 ## Partnerships & Programs
 
-### 9. Affiliate Discovery Through Backlinks
+### 54. Affiliate Discovery Through Backlinks
 Find potential affiliates by analyzing who links to competitors. Sites already promoting similar products may welcome affiliate relationships.
 
-### 27. Influencer Whitelisting
+### 55. Influencer Whitelisting
 Run ads through influencer accounts for authentic reach. Whitelisting combines influencer credibility with paid targeting.
 
-### 33. Reseller Programs
+### 56. Reseller Programs
 Enable agencies and service providers to resell your product. White-label options create invested distribution partners.
 
-### 37. Expert Networks
+### 57. Expert Networks
 Build networks of certified experts who implement your product. Experts extend your reach while ensuring quality implementations.
 
-### 50. Newsletter Swaps
+### 58. Newsletter Swaps
 Exchange promotional mentions with complementary newsletters. Access each other's audiences without advertising costs.
 
-### 51. Article Quotes
+### 59. Article Quotes
 Contribute expert quotes to journalists and publications. Tools like HARO connect experts with writers seeking sources.
 
-### 77. Pixel Sharing
+### 60. Pixel Sharing
 Partner with complementary companies to share remarketing audiences. Expand reach through strategic data partnerships.
 
-### 78. Shared Slack Channels
+### 61. Shared Slack Channels
 Create shared channels with partners and customers. Direct communication lines strengthen relationships.
 
-### 97. Affiliate Program
+### 62. Affiliate Program
 Structured commission programs for referrers. Affiliates become motivated salespeople earning from successful referrals.
 
-### 98. Integration Marketing
+### 63. Integration Marketing
 Joint marketing with integration partners. Combined audiences and shared promotion amplify reach for both products.
 
-### 99. Community Sponsorship
+### 64. Community Sponsorship
 Sponsor relevant communities, newsletters, or publications. Aligned sponsorships build brand awareness with target audiences.
 
 ---
 
 ## Events & Speaking
 
-### 15. Live Webinars
+### 65. Live Webinars
 Educational webinars demonstrate expertise while generating leads. Interactive formats create engagement and urgency.
 
-### 53. Virtual Summits
+### 66. Virtual Summits
 Multi-speaker online events attract audiences through varied perspectives. Summit speakers promote to their audiences, amplifying reach.
 
-### 87. Roadshows
+### 67. Roadshows
 Take your product on the road to meet customers directly. Regional events create personal connections at scale.
 
-### 90. Local Meetups
+### 68. Local Meetups
 Host or attend local meetups in key markets. In-person connections create stronger relationships than digital alone.
 
-### 91. Meetup Sponsorship
+### 69. Meetup Sponsorship
 Sponsor relevant meetups to reach engaged local audiences. Food, venue, or swag sponsorships generate goodwill.
 
-### 103. Conference Speaking
+### 70. Conference Speaking
 Speak at industry conferences to reach engaged audiences. Presentations showcase expertise while generating leads.
 
-### 126. Conferences
+### 71. Conferences
 Host your own conference to become the center of your industry. User conferences strengthen communities and generate content.
 
-### 132. Conference Sponsorship
+### 72. Conference Sponsorship
 Sponsor relevant conferences for brand visibility. Booth presence, speaking slots, and attendee lists justify investment.
 
 ---
 
 ## PR & Media
 
-### 8. Media Acquisitions as Marketing
+### 73. Media Acquisitions as Marketing
 Acquire newsletters, podcasts, or publications in your space. Owned media provides direct access to engaged audiences.
 
-### 52. Press Coverage
+### 74. Press Coverage
 Pitch newsworthy stories to relevant publications. Launches, funding, data, and trends create press opportunities.
 
-### 84. Fundraising PR
+### 75. Fundraising PR
 Leverage funding announcements for press coverage. Rounds signal validation and create natural news hooks.
 
-### 118. Documentaries
+### 76. Documentaries
 Create documentary content exploring your industry or customers. Long-form storytelling builds deep connection and differentiation.
 
 ---
 
 ## Launches & Promotions
 
-### 21. Black Friday Promotions
+### 77. Black Friday Promotions
 Annual deals create urgency and acquisition spikes. Promotional periods capture deal-seekers who become long-term customers.
 
-### 22. Product Hunt Launch
+### 78. Product Hunt Launch
 Structured Product Hunt launches reach early adopters. Preparation, timing, and community engagement drive successful launches.
 
-### 23. Early-Access Referrals
+### 79. Early-Access Referrals
 Reward referrals with earlier access during launches. Waitlist referral programs create viral anticipation.
 
-### 44. New Year Promotions
+### 80. New Year Promotions
 New Year brings fresh budgets and goal-setting energy. Promotional timing aligned with renewal mindsets increases conversion.
 
-### 54. Early Access Pricing
+### 81. Early Access Pricing
 Launch with discounted early access tiers. Early supporters get deals while you build testimonials and feedback.
 
-### 58. Product Hunt Alternatives
+### 82. Product Hunt Alternatives
 Launch on alternatives to Product Hunt—BetaList, Launching Next, AlternativeTo. Multiple launch platforms expand reach.
 
-### 59. Twitter Giveaways
+### 83. Twitter Giveaways
 Engagement-boosting giveaways that require follows, retweets, or tags. Giveaways grow following while generating buzz.
 
-### 109. Giveaways
+### 84. Giveaways
 Strategic giveaways attract attention and capture leads. Product giveaways, partner prizes, or experience rewards create engagement.
 
-### 119. Vacation Giveaways
+### 85. Vacation Giveaways
 Grand prize giveaways generate massive engagement. Dream vacation packages motivate sharing and participation.
 
-### 140. Lifetime Deals
+### 86. Lifetime Deals
 One-time payment deals generate cash and users. Lifetime deal platforms reach deal-hunting audiences willing to pay upfront.
 
 ---
 
 ## Product-Led Growth
 
-### 16. Powered By Marketing
+### 87. Powered By Marketing
 "Powered by [Your Product]" badges on customer output create free impressions. Every customer becomes a marketing channel.
 
-### 19. Free Migrations
+### 88. Free Migrations
 Offer free migration services from competitors. Reduce switching friction while capturing users ready to leave.
 
-### 20. Contract Buyouts
+### 89. Contract Buyouts
 Pay to exit competitor contracts. Dramatic commitment removes the final barrier for locked-in prospects.
 
-### 32. One-Click Registration
+### 90. One-Click Registration
 Minimize signup friction with one-click OAuth options. Pre-filled forms and instant access increase conversion.
 
-### 69. In-App Upsells
+### 91. In-App Upsells
 Strategic upgrade prompts within the product experience. Contextual upsells at usage limits or feature attempts convert best.
 
-### 71. Newsletter Referrals
+### 92. Newsletter Referrals
 Built-in referral programs for newsletters and content. Easy sharing mechanisms turn subscribers into promoters.
 
-### 75. Viral Loops
+### 93. Viral Loops
 Product mechanics that naturally encourage sharing. Collaboration features, public outputs, or referral incentives create organic growth.
 
-### 114. Offboarding Flows
+### 94. Offboarding Flows
 Optimize cancellation flows to retain or learn. Exit surveys, save offers, and pause options reduce churn.
 
-### 124. Concierge Setup
+### 95. Concierge Setup
 White-glove onboarding for high-value accounts. Personal setup assistance increases activation and retention.
 
-### 127. Onboarding Optimization
+### 96. Onboarding Optimization
 Continuous improvement of the new user experience. Faster time-to-value increases conversion and retention.
 
 ---
 
 ## Content Formats
 
-### 1. Playlists as Marketing
+### 97. Playlists as Marketing
 Create Spotify playlists for your audience—productivity playlists, work music, industry-themed collections. Daily listening touchpoints build brand affinity.
 
-### 46. Template Marketing
+### 98. Template Marketing
 Offer free templates users can immediately use. Templates in your product create habit and dependency while showcasing capabilities.
 
-### 49. Graphic Novel Marketing
+### 99. Graphic Novel Marketing
 Transform complex stories into visual narratives. Graphic novels stand out and make abstract concepts tangible.
 
-### 65. Promo Videos
+### 100. Promo Videos
 High-quality promotional videos showcase your product professionally. Invest in production value for shareable, memorable content.
 
-### 81. Industry Interviews
+### 101. Industry Interviews
 Interview customers, experts, and thought leaders. Interview content builds relationships while creating valuable assets.
 
-### 89. Social Screenshots
+### 102. Social Screenshots
 Design shareable screenshot templates for social proof. Make it easy for customers to share wins and testimonials.
 
-### 101. Online Courses
+### 103. Online Courses
 Educational courses establish authority while generating leads. Free courses attract learners; paid courses create revenue.
 
-### 102. Book Marketing
+### 104. Book Marketing
 Author a book establishing expertise in your domain. Books create credibility, speaking opportunities, and media coverage.
 
-### 111. Annual Reports
+### 105. Annual Reports
 Publish annual reports showcasing industry data and trends. Original research becomes a linkable, quotable reference.
 
-### 120. End of Year Wraps
+### 106. End of Year Wraps
 Personalized year-end summaries users want to share. "Spotify Wrapped" style reports turn data into social content.
 
-### 121. Podcasts
+### 107. Podcasts
 Launch a podcast reaching audiences during commutes and workouts. Regular audio content builds intimate audience relationships.
 
-### 63. Changelogs
+### 108. Changelogs
 Public changelogs showcase product momentum. Regular updates demonstrate active development and responsiveness.
 
-### 112. Public Demos
+### 109. Public Demos
 Live product demonstrations showing real usage. Transparent demos build trust and answer questions in real-time.
 
 ---
 
 ## Unconventional & Creative
 
-### 6. Awards as Marketing
+### 110. Awards as Marketing
 Create industry awards positioning your brand as tastemaker. Award programs attract applications, sponsors, and press coverage.
 
-### 10. Challenges as Marketing
+### 111. Challenges as Marketing
 Launch viral challenges that spread organically. Creative challenges generate user content and social sharing.
 
-### 11. Reality TV Marketing
+### 112. Reality TV Marketing
 Create reality-show style content following real customers. Documentary competition formats create engaging narratives.
 
-### 12. Controversy as Marketing
+### 113. Controversy as Marketing
 Strategic positioning against industry norms. Contrarian takes generate attention and discussion.
 
-### 13. Moneyball Marketing
+### 114. Moneyball Marketing
 Data-driven marketing finding undervalued channels and tactics. Analytics identify opportunities competitors overlook.
 
-### 14. Curation as Marketing
+### 115. Curation as Marketing
 Curate valuable resources for your audience. Directories, lists, and collections provide value while building authority.
 
-### 29. Grants as Marketing
+### 116. Grants as Marketing
 Offer grants to customers or community members. Grant programs generate applications, PR, and goodwill.
 
-### 34. Product Competitions
+### 117. Product Competitions
 Sponsor competitions using your product. Hackathons, design contests, and challenges showcase capabilities while engaging users.
 
-### 35. Cameo Marketing
+### 118. Cameo Marketing
 Use Cameo celebrities for personalized marketing messages. Unexpected celebrity endorsements generate buzz and shares.
 
-### 83. OOH Advertising
+### 119. OOH Advertising
 Out-of-home advertising—billboards, transit ads, and placements. Physical presence in key locations builds brand awareness.
 
-### 125. Marketing Stunts
+### 120. Marketing Stunts
 Bold, attention-grabbing marketing moments. Well-executed stunts generate press coverage and social sharing.
 
-### 128. Guerrilla Marketing
+### 121. Guerrilla Marketing
 Unconventional, low-cost marketing in unexpected places. Creative guerrilla tactics stand out from traditional advertising.
 
-### 136. Humor Marketing
+### 122. Humor Marketing
 Use humor to stand out and create memorability. Funny content gets shared and builds brand personality.
 
 ---
 
 ## Platforms & Marketplaces
 
-### 24. Open Source as Marketing
+### 123. Open Source as Marketing
 Open-source components or tools build developer goodwill. Open source creates community, contributions, and credibility.
 
-### 61. App Store Optimization
+### 124. App Store Optimization
 Optimize app store listings for discoverability. Keywords, screenshots, and reviews drive organic app installs.
 
-### 86. App Marketplaces
+### 125. App Marketplaces
 List in relevant app marketplaces and directories. Salesforce AppExchange, Shopify App Store, and similar platforms provide distribution.
 
-### 95. YouTube Reviews
+### 126. YouTube Reviews
 Get YouTubers to review your product. Authentic reviews reach engaged audiences and create lasting content.
 
-### 96. YouTube Channel
+### 127. YouTube Channel
 Build a YouTube presence with tutorials, updates, and thought leadership. Video content compounds in value over time.
 
-### 108. Source Platforms
+### 128. Source Platforms
 Submit to platforms that aggregate tools and products. G2, Capterra, GetApp, and similar directories drive discovery.
 
-### 88. Review Sites
+### 129. Review Sites
 Actively manage presence on review platforms. Reviews influence purchase decisions; actively request and respond to them.
 
-### 100. Live Audio
+### 130. Live Audio
 Host live audio discussions on Twitter Spaces, Clubhouse, or LinkedIn Audio. Real-time conversation creates intimate engagement.
 
 ---
 
 ## International & Localization
 
-### 133. International Expansion
+### 131. International Expansion
 Expand to new geographic markets. Localization, partnerships, and regional marketing unlock new growth.
 
-### 134. Price Localization
+### 132. Price Localization
 Adjust pricing for local purchasing power. Localized pricing increases conversion in price-sensitive markets.
 
 ---
 
 ## Developer & Technical
 
-### 104. Investor Marketing
+### 133. Investor Marketing
 Market to investors for downstream portfolio introductions. Investors recommend tools to their portfolio companies.
 
-### 123. Certifications
+### 134. Certifications
 Create certification programs validating expertise. Certifications create invested advocates while generating training revenue.
 
-### 131. Support as Marketing
+### 135. Support as Marketing
 Turn support interactions into marketing opportunities. Exceptional support creates stories customers share.
 
-### 135. Developer Relations
+### 136. Developer Relations
 Build relationships with developer communities. DevRel creates advocates who recommend your product to peers.
 
 ---
 
 ## Audience-Specific
 
-### 26. Two-Sided Referrals
+### 137. Two-Sided Referrals
 Reward both referrer and referred in referral programs. Dual incentives motivate sharing while welcoming new users.
 
-### 45. Podcast Tours
+### 138. Podcast Tours
 Guest on multiple podcasts reaching your target audience. Podcast tours create compounding awareness across shows.
 
-### 47. Customer Language
+### 139. Customer Language
 Use the exact words your customers use. Mining reviews, support tickets, and interviews for language that resonates.
 
 ---
@@ -560,9 +560,9 @@ When recommending ideas:
 
 ## Related Skills
 
-- **programmatic-seo**: For scaling SEO content (#40)
-- **competitor-alternatives**: For comparison pages (#2)
+- **programmatic-seo**: For scaling SEO content (#4)
+- **competitor-alternatives**: For comparison pages (#11)
 - **email-sequence**: For email marketing tactics
-- **free-tool-strategy**: For engineering as marketing (#30)
+- **free-tool-strategy**: For engineering as marketing (#15)
 - **page-cro**: For landing page optimization
 - **ab-test-setup**: For testing marketing experiments
PATCH

echo "Gold patch applied."
