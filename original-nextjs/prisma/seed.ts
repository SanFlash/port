import { PrismaClient, Visibility } from "@prisma/client";
const db = new PrismaClient();
const items = [
 ["role","Brand Strategist",{}],["role","Social Media & Digital Marketing Strategist",{}],["role","Design Researcher",{}],
 ["experience","Brand Strategist | Social Media & Content",{organization:"AAROhan Agri Products",dates:"Jan - Jun 2026",description:"Built the brand's digital presence, voice, visual identity and social content strategy for an early-stage agri-product business."}],
 ["experience","Brand & Communication Researcher",{organization:"Foundation for MSME Clusters",dates:"Apr - Jul 2025",description:"Led field research across 40+ artisan interviews for the SFURTI scheme."}],
 ["experience","Project Manager - Brand & Communication",{organization:"SFURTI Scheme, Government of India",dates:"Jun 2023 - May 2024",description:"Directed a government-funded craft cluster programme across 5 MP districts."}],
 ["experience","Content & SEO Executive",{organization:"Candent SEO (Remote)",dates:"Feb - May 2021",description:"Produced SEO-optimised articles across client brands using keyword research and search-intent principles."}],
 ["experience","Fashion & Visual Design Intern",{organization:"Samarth Scheme, Government of India",dates:"Jan - Jul 2020",description:"Developed craft-based garment and textile designs for a ministry showcase."}],
 ["project","TEEJH",{description:"Brand positioning and go-to-market strategy for an ethnic jewellery brand using the Brand Prism framework."}],
 ["project","TalkItOut Community",{description:"Community-first brand identity addressing Gen Z mental-health trust barriers via Brand Archetypes."}],
 ["project","Bhuttico",{description:"Ethnographic research across a weaving ecosystem to identify branding and digital opportunities."}],
 ["education","Master of Design (M.Des.) - Strategy Design",{institution:"National Institute of Fashion Technology (NIFT), Bhopal",date:"May 2026"}],
 ["education","Diploma - Textile Product Development, Apparel & Textiles",{institution:"Graffiti Institute of Fashion Technology",date:"May 2022"}],
 ["education","B.A. (Hons.) - Fashion Design",{institution:"Institute for Excellence in Higher Education (IEHE), Bhopal",date:"May 2019",grade:"81.4%"}],
 ["social","Behance",{url:"https://www.behance.net/falgunichouhan"}],["youtube","Toddland World",{url:"https://www.youtube.com/@ToddlandWorld"}],["youtube","Toonzeekidz",{url:"https://www.youtube.com/@Toonzeekidz"}]
] as const;
async function main(){ await db.profile.upsert({where:{id:"profile"},update:{},create:{id:"profile",name:"Falguni Chauhan",headline:"Social Media & Digital Marketing Strategist",location:"Bhopal, Madhya Pradesh, India",email:"falgunichouhan1234@gmail.com",phone:"+91 78048 83067",intro:"Building brands, growing digital communities, and driving content-led marketing.",summary:"Social Media & Digital Marketing Strategist with experience across commercial, artisan, government, and community sectors."}}); for (const [collection,title,data] of items) await db.collectionItem.upsert({where:{slug:`${collection}-${title}`.toLowerCase().replace(/[^a-z0-9]+/g,"-")},update:{},create:{collection,title,slug:`${collection}-${title}`.toLowerCase().replace(/[^a-z0-9]+/g,"-"),data,status:Visibility.PUBLISHED}}) }
main().finally(()=>db.$disconnect());
