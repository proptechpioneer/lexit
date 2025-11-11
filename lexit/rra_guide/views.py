from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def rra_guide_home(request):
    """
    Main RRA Guide home page with welcome section and navigation to all guide sections
    """
    
    # Define all sections for the guide
    sections = [
        {
            'id': 'financial_model',
            'title': 'Financial Model',
            'icon': 'fas fa-chart-line',
            'description': 'Understanding the financial implications and cost structure'
        },
        {
            'id': 'property_scope',
            'title': 'Which Properties Does the RRA Apply To?',
            'icon': 'fas fa-home',
            'description': 'Scope and applicability of the Renters Rights Act'
        },
        {
            'id': 'tenancy_abolition',
            'title': 'Abolition of Assured Shorthold Tenancies',
            'icon': 'fas fa-file-contract',
            'description': 'Changes to tenancy structures and agreements'
        },
        {
            'id': 'ending_tenancy',
            'title': 'Ending a Tenancy',
            'icon': 'fas fa-door-open',
            'description': 'New procedures and requirements for tenancy termination'
        },
        {
            'id': 'rent_setting',
            'title': 'Setting and Increasing the Rent',
            'icon': 'fas fa-pound-sign',
            'description': 'New rules for rent setting and increases'
        },
        {
            'id': 'discrimination',
            'title': 'Prohibition on Discrimination',
            'icon': 'fas fa-balance-scale',
            'description': 'Anti-discrimination rules for benefits recipients and families'
        },
        {
            'id': 'pets',
            'title': 'Pets',
            'icon': 'fas fa-paw',
            'description': 'New regulations regarding pets in rental properties'
        },
        {
            'id': 'database',
            'title': 'New Private Rented Sector Database',
            'icon': 'fas fa-database',
            'description': 'Registration requirements and compliance'
        },
        {
            'id': 'penalties',
            'title': 'Penalties for Non-Compliance',
            'icon': 'fas fa-exclamation-triangle',
            'description': 'Understanding fines and enforcement actions'
        },
        {
            'id': 'timing',
            'title': 'Timing',
            'icon': 'fas fa-calendar-alt',
            'description': 'Implementation timeline and key dates'
        },
        {
            'id': 'awaabs_law',
            'title': "Awaab's Law and Decent Homes Standard",
            'icon': 'fas fa-shield-alt',
            'description': 'Housing standards and safety requirements'
        }
    ]
    
    # Welcome content for the home page
    welcome_content = {
        'title': 'Renters\' Rights Act - Landlord Information Centre',
        'subtitle': 'Your comprehensive guide to understanding and complying with the new legislation',
        'introduction': [
            'The Renters\' Rights Act (RRA) passed through English parliament on 27 October 2025 and will lead to the biggest shake-up of the private rental market in England in a generation.',
            'The shift will be structural, transformational and the changes will be permanent. The introduction of the RRA has already had significant consequences for the English rental market:'
        ],
        'key_impacts': [
            'Small landlords are selling up',
            'Professional investors are scaling up', 
            'The rules have completely changed'
        ],
        'context_note': 'These trends will continue as the balance of power in the rental market firmly moves from landlords to tenants. It is important that landlords are prepared for the new regime given the extent of the changes and the fact that certain provisions require action within a short timeframe of the RRA coming into force.',
        'landlord_focus': {
            'title': 'Renters\' Rights Act 2025 for Landlords',
            'content': [
                'The Renters\' Rights Act fundamentally changes the role of the landlord in Buy-to-Let relationships. The RRA makes the role of the landlord more akin to a service provider such as a hotelier rather than a traditional landlord in the way which many landlords are used to.',
                'Tenants have far greater rights and the balance of power now sits with them rather than the landlord. Landlords have a legal obligation to meet the requirements of the Act, which it cannot pass on to a third party such as a property manager.',
                'Failure to meet the standards now has significant financial and criminal penalties for landlords. These include:'
            ],
            'penalties': [
                'Fines and penalties of between £2,000 - £7,000 (per breach)',
                'The ability of the tenant to recover two years rental at any point including up to 2 years after the end of the tenancy'
            ]
        }
    }
    
    context = {
        'sections': sections,
        'total_sections': len(sections),
        'welcome_content': welcome_content
    }
    
    return render(request, 'rra_guide/home.html', context)

@login_required
def rra_section_detail(request, section_id):
    """
    Display detailed information for a specific RRA section
    """
    
    # Define all section content
    section_content = {
        'financial_model': {
            'title': 'Financial Model',
            'explainer': {
                'title': 'Understanding the Financial Impact of the Renters Rights Act',
                'content': [
                    'The first step to reviewing the impact of the Renters\' Rights Act on your property or property portfolio is to build a financial picture of your property investment(s).',
                    'Without a detailed knowledge of the potential financial output of your investment, it is impossible to determine whether or not the RISK created by the Renters Right Act is worth accepting relative to the potential REWARD your investment may generate.',
                    'Users can use the LEXIT platform to analyse their property (or portfolio), simply select the "Analyse a Property" button to analyse your property now.',
                    'If you don\'t want to use the platform you should still undertake this work yourself. Your financial analysis needs to consider the investment from an after-tax perspective and should consider the following:',
                    '• Current Net Return (after tax) as a % of the capital you have invested',
                    '• Forecast Net Income (after tax) over the medium to long-term',
                    '• Estimated Capital Appreciation (after tax) in the event the property is sold',
                    'As a minimum these measures will help you understand the financial reality of your investment and to compare this to alternative investments.',
                    'NOTE: you should ensure your analysis realistically considers growth and expenses.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Investment Reality Check:</strong> Many landlords will likely find that the return or potential return from the property does not make sense relative to the potential risk imposed on them under the Renters\' Rights Act.',
                    '<strong>1. Compromised Rental Income:</strong> Compromised ability to increase the rental income in response to market conditions and cost inflation, limiting your ability to maintain returns in real terms.',
                    '<strong>2. Reduced Income Certainty:</strong> Term certain income reduced by the loss of fixed term tenancies, making cash flow planning more difficult and increasing vacancy risk.',
                    '<strong>3. Penalty Exposure:</strong> Exposure to increased fines for breaches of the new rules, with civil penalties of up to £7,000 per violation significantly impacting annual returns.',
                    '<strong>4. Rent Recovery Risk:</strong> Ability for the tenant to recover up to 2 years rent for certain breaches of the new rules, potentially creating liability of £24,000+ per property.',
                    '<strong>Registration Costs:</strong> Annual fees estimated at £40-£80 per property, with initial setup costs of £150-£300 per portfolio. Late registration penalties of up to £5,000 per property.',
                    '<strong>Compliance Infrastructure:</strong> Professional property management software (£20-£50/month), legal compliance reviews (£500-£1,500 annually), enhanced insurance premiums (10-15% increase expected).',
                    '<strong>Extended Void Periods:</strong> Tenancy security means longer void periods when properties become vacant. Budget for an additional 2-3 weeks void time per turnover, costing £200-£500 per week in lost rent.',
                    '<strong>Legal and Professional Costs:</strong> Tenancy termination may require legal representation (£1,500-£5,000 per case), property condition assessments (£200-£400 annually), and compliance documentation (£300-£600 annually).'
                ]
            }
        },
        'property_scope': {
            'title': 'Which Properties Does the RRA Apply To?',
            'explainer': {
                'title': 'Understanding Which Properties Are Impacted',
                'content': [
                    'Which properties will be impacted by the Renters\' Rights Act? Essentially, all properties in the Private Rented Sector will be subject to the Renters\' Rights Act, this will include all residential properties let under Assured Shorthold Tenancies.',
                    'What is the Private Rented Sector? The Private Rented Sector (PRS) is a classification of housing in the UK. The basic Private Rented Sector definition is: property owned by a landlord and leased to a tenant. The landlord, can be an individual, a property company or an institutional investor. It makes no difference whether the tenants deal directly a property management company, estate agency, or deal with the landlord directly.',
                    'The PRS is the fastest-growing sector in England and is the second largest housing tenure, with owner-occupation currently being the largest. The sector originally accounted for just a small percentage of the UK housing market, but the number of households in the Private Rented Sector (PRS) has doubled in just over a decade and continues to grow. Some reports suggest that 40% of London\'s households could be renting in the PRS by 2030.',
                    'The rapid growth of the PRS, means that more and more people are living in rented accommodation in England. As new housing supply has stalled it has had a dramatic impact on housing affordability, which is the reason the government is now intervening in the rental market.',
                    'Tenancies that are not caught by the Act: The RRA will not affect tenancies that are not assured tenancies such as common law residential tenancies, for example, where the tenant is a corporate or where the annual rent is more than £100,000. They will also not affect genuine licences to occupy.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Scope of Impact:</strong> For most landlords your property is likely subject to the Renters\' Rights Act which means that you will have to significantly alter the way you manage your property.',
                    '<strong>Property Coverage Check:</strong> You need to check whether or not your property is covered under the new Act, as some properties are exempt from the Renters\' Rights Act.',
                    '<strong>Exempt Properties:</strong> The following property types are exempt from the Renters\' Rights Act:',
                    '• <strong>Purpose Build Student Accommodation (PBSA):</strong> Specifically designed student housing developments remain outside the scope of the Act.',
                    '• <strong>Non-Residential Lets:</strong> Commercial properties and mixed-use properties where the primary use is not residential.',
                    '• <strong>Short-term Holiday Lets:</strong> Properties used for tourism and short-term accommodation (typically under 90 days).',
                    '• <strong>Lodger Agreements:</strong> Where tenants share accommodation with the landlord in their main residence.',
                    '• <strong>Properties in Wales and Scotland:</strong> The Act applies only to England - Wales and Scotland have separate legislation.',
                    '• <strong>Social Housing:</strong> Council housing and housing association properties are covered by different regulations.',
                    '<strong>High-Value Exemptions:</strong> Properties with annual rent exceeding £100,000 and corporate tenancies fall outside assured tenancy rules and therefore outside the RRA scope.',
                    '<strong>Action Required:</strong> Conduct a portfolio review to identify which properties are covered and which are exempt to ensure appropriate compliance measures are implemented only where necessary.'
                ]
            }
        },
        'tenancy_abolition': {
            'title': 'Abolition of Assured Shorthold Tenancies',
            'explainer': {
                'title': 'Understanding the End of ASTs',
                'content': [
                    'Since February 1997, the most commonly used form of residential tenancy in England has been the Assured Shorthold Tenancy often referred to as ASTs. A major change implemented by the Renters\' Rights Act is that it abolishes ASTs.',
                    'What is an Assured Shorthold Tenancy (AST)? The vast majority of tenancies are considered an Assured Shorthold Tenancy (AST). Put simply, it is an agreement between a landlord and a tenant living in a rented property. It is normally a written agreement (but can be verbal) that clearly outlines your responsibilities as landlord.',
                    'A written AST will state the following terms: Start date and end of the fixed-term; Rent to pay; Date rent must be paid; Address of the rented property; Name and address of all parties (e.g. tenant, landlord and letting agent); When and how the rent is reviewed; Deposit amount and the scheme which protects it; When the deposit can be withheld; Bills the tenant is responsible for.',
                    'Abolition of Assured Shorthold Tenancies: The Renters\' Rights Act abolishes Assured Shorthold Tenancies (ASTs) and makes all ASTs periodic tenancies. This means that all tenancies will no longer have a fixed term and that a landlord will only be able to terminate a tenancy for specific reason under section 8 of the Housing Act 1988 (covered later).',
                    'As ASTs will no longer exist, tenants will instead have ATs with the greater security that they provide. Significantly, the Act will also abolish fixed term ATs, so tenants will move to a system of \'rolling\' or periodic ATs. The Housing Act 1988 will continue to refer to them simply as assured tenancies, therefore we will refer to new tenancies as ATs.',
                    'Tenants\' Ability to End a Lease: A tenant on the other hand can leave the property at any time for any reason, by giving a notice to quit. This will normally, but not always, be not less than two months\' notice to expire at the end of a \'rent period\', which is usually a rent payment date.',
                    'What happens to Existing Tenancies? Existing ASTs will automatically be converted into ATs when the RRA comes into force, regardless of the unexpired fixed term remaining at the time the RRA comes into effect. Landlords will not be able to grant new fixed term ASTs after that date and must not purport to do. Landlords who do this will be subject to penalties (see penalties later).'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Fundamental Change:</strong> For landlords the impact of the removal of Assured Shorthold Tenancies is significant. It now means you are effectively renting your property to your current tenant indefinitely, but your tenant can leave at any point by giving 2 months\' notice.',
                    '<strong>Income Security Loss:</strong> This effectively takes away your income security as at any point in time you can only be certain the tenant will be paying rent for the next 2 months.',
                    '<strong>Current Tenant Assessment:</strong> Are you comfortable with your current tenant? Have they always been up to date with the rent? This becomes critically important when you cannot easily end the tenancy.',
                    '<strong>Vacancy Risk:</strong> The tenant\'s right to end the tenancy is an important concern for landlords/investors, since it provides tenants with an opportunity to leave at a very early stage and the rental income from those premises will cease. If you have a tenant vacate a property can you afford to cover a rental void? Remember this includes council tax and other costs not just the mortgage.',
                    '<strong>Churn Costs:</strong> The new Act also means that you could have a tenant leave every two months, creating considerable churn in your property. Not only will this create void periods, you are likely to incur other costs too such as leasing, inventory and referencing costs as well as interim maintenance costs.',
                    '<strong>Strategic Considerations:</strong> Key questions to consider: Can you maintain positive cash flow during void periods? How will frequent tenant turnover affect your property management costs? Do you have reserves to cover the additional administrative and maintenance expenses from increased tenant churn?',
                    '<strong>Legal Compliance:</strong> Ensure you understand that attempting to grant new ASTs after the Act comes into force will result in penalties. All future tenancies must comply with the new AT framework.'
                ]
            }
        },
        'ending_tenancy': {
            'title': 'Ending a Tenancy',
            'explainer': {
                'title': 'New Termination Procedures Under RRA',
                'content': [
                    'Until the introduction of the RRA, the main feature of an AST has been the ability of the landlord to end the tenancy without giving a reason after the end of the fixed term (typically 6 – 12 months). The landlord could, in theory, terminate the tenancy once the fixed term ended by giving not less than two months\' notice under section 21 of the Housing Act 1988 without specifying a reason. This became known as a \'no-fault eviction\' – even though the tenant was not technically being evicted.',
                    'Abolition of section 21 (no-fault) evictions: The flagship reform under the RRA is the abolition of ASTs and, with it, section 21 \'no-fault\' evictions. Landlords will only be able to terminate ATs if they can prove one or more of the statutory grounds for termination. In contrast, tenants will be able to terminate an AT any time by giving two months\' notice. There will be no \'guaranteed\' minimum fixed term, even if both parties want one.',
                    'The RRA makes changes to the existing Section 8 process, seeking to strike a balance between the interests of landlords and tenants. Changes include adjustments to time limits and the introduction of pre-conditions.',
                    'Ending a Tenancy Under RRA: The landlord\'s approach to ending a tenancy should now be seen as a process rather than a one-time event. The recent changes introduced by the Act have expanded the grounds for ending a lease under Section 8 and altered many procedures.',
                    'These grounds act as gateways to court proceedings for possession. If a landlord believes their case fits a valid ground, they can start legal action. However, delays are a concern due to court backlogs in 2025, which could slow down the process. It\'s also uncertain how the new rules will work in practice once they\'re fully implemented.',
                    'Possession grounds are either mandatory or discretionary: Mandatory grounds require the court to grant possession if the landlord proves the ground, but courts might still consider other factors like human rights issues. Discretionary grounds give the court the choice to decide if it\'s reasonable to grant possession, considering all circumstances.',
                    'Importantly, serving a notice based on specific grounds does not guarantee possession. Many grounds have specific exceptions, so professional advice is essential in each case. Some issues involve judgment about the landlord\'s intentions, and how tenants challenge these in court remains to be seen.',
                    'The government recognizes the challenges posed by court delays, especially when landlords need quick solutions for issues like anti-social behaviour affecting others\' safety. They\'ve promised to review and address court backlogs to help landlords handle these situations more effectively.',
                    'Grounds for Serving Notice under RRA: When a landlord decides to end a tenancy (not when a tenant voluntarily chooses to leave), under the RRA: A valid Section 8 notice must be served; Serving a defective notice is an offence; If a tenant leaves after receiving the notice (without the case going to court), the landlord (and/or their letting agent) can be fined if they used grounds they could not legally rely on — whether through negligence or on purpose; To reduce risk, it may be better for landlords to work with a solicitor to serve notices on their behalf.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Loss of Section 21:</strong> As a landlord you will no longer be able to terminate your tenants lease via section 21 ground, taking away the main advantage of this tenancy for landlords. Instead, you will need to use a section 8 possession grounds under the Housing Act 1988.',
                    '<strong>Expanded Section 8 Grounds:</strong> The section 8 grounds will be expanded to enable landlords to recover their property when reasonable, for example, to sell or move in. Despite these additional possession grounds, removal of the section 21 ground of termination will make it more difficult for landlords to regain possession of their property.',
                    '<strong>Key Mandatory Grounds:</strong> Ground 1 (landlord/family occupation - 4 months notice, 16-month re-letting restriction); Ground 1A (sale - 4 months notice, 16-month restriction); Ground 8 (severe rent arrears - 4 weeks notice); Ground 6 (redevelopment - 4 months notice).',
                    '<strong>Key Discretionary Grounds:</strong> Ground 10 (rent arrears - 4 weeks notice); Ground 11 (persistent late payment - 4 weeks notice); Ground 12 (breach of contract - 2 weeks notice); Ground 14 (nuisance/ASB - no notice required).',
                    '<strong>Legal Compliance Risks:</strong> Serving defective notices is an offence. Fines apply if tenants leave based on invalid grounds, whether through negligence or intentional misuse.',
                    '<strong>Professional Support Required:</strong> Consider working with solicitors to serve notices and reduce legal risks. Professional advice essential for each case due to specific exceptions and requirements.',
                    '<strong>Court Delays:</strong> Expect longer possession processes due to court backlogs. Plan for extended timelines when needing to regain possession.',
                    '<strong>Re-letting Restrictions:</strong> Grounds 1 and 1A include 16-month total restrictions on marketing and re-letting (from notice service until 12 months after notice expires).',
                    '<strong>Process Management:</strong> Treat tenancy termination as a process requiring careful documentation, proper notice periods, and potentially court proceedings rather than automatic possession recovery.'
                ]
            }
        },
        'rent_setting': {
            'title': 'Setting and Increasing the Rent',
            'explainer': {
                'title': 'New Rent Control Mechanisms Under RRA',
                'content': [
                    'The Renters\' Rights Act introduces a number of new elements with respect to how much rent landlords can charge tenants and when and how they can increase the rent.',
                    'Under the RRA all advertisements for a property for rent must state the rent. Tenants may bid up to, but not above the advertised rent. A Tenant will now be able to request a rent reduction within 6 months if the rent is above market rent.',
                    'Landlords must now think carefully about how they price their property: All adverts must contain a written rental figure – which represents the absolute maximum which can be charged; Bidding can be encouraged up to this figure but not above it.',
                    'Prohibition on rent \'bidding wars\': The Act will outlaw so-called rent \'bidding wars\'. Any advert to let a property on an APT must specify the proposed rent. Once specified, landlords and agents must not invite, encourage or accept offers of rent higher than the advertised sum. This may mean that new schemes are launched on a phased basis to allow landlords to "test" the market without committing significant numbers of units to the advertised rental level.',
                    'Increasing the Rent – Section 13: Landlords of APTs will only be able to increase the rent by following a revised statutory procedure in Section 13 of Housing Act 1988. Any contractual rent reviews, whether open market or index-linked, or pre-fixed uplifts – will be unenforceable.',
                    'Section 13 allows the landlord to increase the rent once a year on two months\' notice to begin at the start of a new \'rent period\'. However, tenants can challenge excessive increases in the First-Tier Tribunal (FTT).',
                    'The FTT will no longer be able to order a rent higher than the rent proposed in the landlord\'s notice, even if it is found to be below market rent at the point of the FTT\'s decision. The new rent will only take effect after the rent has been determined by the FTT and will not be backdated to the date of the landlord\'s notice.',
                    'Many investors have expressed concerns about the rent increases provisions of the RRA, on the basis that they give tenants a positive incentive to challenge even legitimate market increases, as well as about how delays in determining and giving effect to rent increase will disturb rent review cycles. There will also likely be costs to landlords too associated with implementing uplifts where challenges do arise.',
                    'Advance rental payments: The Act will prohibit landlords and agents from inviting, encouraging or accepting any rent or offer to pay it before the tenancy is entered into, even if unsolicited. This will not prevent landlords or agents continuing to accept a refundable holding deposit of up to one week\'s rent, but it will have some practical consequences.',
                    'Payments in advance under tenancy once entered into: For new ATs entered into after the RRA comes into force, the tenant cannot be required to pay rent before the start of the rent period to which it relates. This does not mean that rent must be payable in arrears, but it does mean that rent cannot be payable more than a month in advance, a month being the maximum rent period allowed.',
                    'If, once the tenancy is entered into, the tenant chooses to pay more than a month in advance, the landlord can accept the advance rent, but the AT cannot require the tenant to pay this way. Any such term will be unenforceable and read as requiring payment later, usually on the first day of each rent period.',
                    'The only exception to the rent payable in advance rule is where a tenancy is entered into before the term begins. In that situation, the AT can require rent for the first period to be paid after the tenancy is entered into but before the term begins. However, the first rent payment cannot be accepted by the landlord or agent until after the tenancy agreement is entered into because of the prohibition on pre-tenancy payments described above.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Rental Growth Moderation:</strong> The new rules will not amount to a rent cap per se, however, they are anticipated to significantly moderate future rental growth.',
                    '<strong>Challenge Expectation:</strong> Landlords should anticipate much slower rental growth and that any proposed rental increase will be challenged by the tenant. If challenged it is anticipated that the proposed rental increase will take a considerable time to be agreed (current estimates are 12 – 15 months).',
                    '<strong>No Backdating:</strong> Even if the tribunal does agree that the landlords estimate of the market rent is correct, the rental increase will not be backdated. In addition, the FTT will not increase the rent above the amount requested by the tenant, even if it concludes that amount is below the actual market rent.',
                    '<strong>Financial Planning Adjustments:</strong> Accordingly landlords should consider the following: Adjust their financial forecasts for rental growth to assume much slower rental growth (or none); Anticipate that rental growth is delayed as any section 13 issued by a landlord will likely be challenged by the tenant, especially given the UK\'s lacklustre economic growth.',
                    '<strong>Advertising Restrictions:</strong> All rental advertisements must state a maximum rent figure. No bidding above advertised rent is permitted, removing the ability to capitalize on high-demand markets through competitive bidding.',
                    '<strong>Advance Payment Limitations:</strong> Cannot accept any rent payments before tenancy agreement is signed. Maximum advance payment once tenancy begins is one month, limiting cash flow advantages from advance payments.',
                    '<strong>Section 13 Process Changes:</strong> Annual rent increases limited to Section 13 procedure only. Contractual rent review clauses become unenforceable. Two months\' notice required for any increase.',
                    '<strong>Tribunal Risks:</strong> FTT cannot award rent higher than landlord\'s notice, even if market rent justifies it. This creates a asymmetric risk where landlords can only lose from tribunal decisions.',
                    '<strong>Market Testing Strategy:</strong> Consider phased launches for new developments to test market rates without committing large numbers of units to potentially below-market advertised rents.',
                    '<strong>Government Intervention Risk:</strong> Even though the government has said they may well intervene, in the event the First Tier Tribunal is overwhelmed and introduce some type of market mechanism, landlords need to consider that given the one-sided nature of the Act, it seems unlikely that such a mechanism will be in the benefit of landlords.'
                ]
            }
        },
        'discrimination': {
            'title': 'Prohibition on Discrimination Against Tenants on Benefits or with Children',
            'explainer': {
                'title': 'Anti-Discrimination Rules Under RRA',
                'content': [
                    'The RRA will outlaw discriminatory practices by landlords and agents against tenants with children or those claiming benefits (often referred to a DSS). This captures blanket policies that would deter such tenants from enquiring about a property or renting it, such as adverts stipulating \'No children or DSS\'.',
                    'However, discrimination is permitted where necessary to comply with an existing insurance policy for the property in place when the RRA comes into force or in relation to tenants with children where it is "a proportionate means of achieving a legitimate aim". The example given in the explanatory notes to the RRA is barring a tenant with two teenage children from renting a small bedroom in an HMO where that would result in overcrowding.',
                    'Corresponding discriminatory terms in tenancy agreements, superior leases and mortgages, and in new insurance policies entered into or extended after the RRA is in force, which would require the borrower or the insured to discriminate against such tenants, will be unenforceable when the Act takes effect.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Acceptance Requirement:</strong> Whilst it is unlikely that most landlords will have a significant issue with being forced to accept tenants they don\'t want to as an oversupply of tenants will likely counteract any significant risk.',
                    '<strong>Written Policy Requirement:</strong> However, it would be prudent for most landlords to have a written policy which guides their tenant selection. Further landlords will need to be able to demonstrate they are following their policy in the case of a dispute.',
                    '<strong>Advertising Changes:</strong> Remove any discriminatory language from property advertisements. Cannot include "No DSS", "No children", or similar exclusionary statements.',
                    '<strong>Selection Criteria Documentation:</strong> Develop objective, non-discriminatory tenant selection criteria based on legitimate factors such as income verification, credit history, and references.',
                    '<strong>Insurance Policy Review:</strong> Existing insurance policies in place before RRA may provide exemptions for discrimination requirements. Review current policies and understand any obligations they impose.',
                    '<strong>Legitimate Aim Exceptions:</strong> Understand when discrimination may be permitted as "proportionate means of achieving legitimate aim" - typically related to overcrowding, safety, or specific property characteristics.',
                    '<strong>Training Requirements:</strong> Ensure letting agents and property managers understand the new discrimination rules and can apply tenant selection policies consistently and legally.',
                    '<strong>Legal Compliance:</strong> New insurance policies, tenancy agreements, and mortgages entered after RRA cannot include discriminatory terms requiring exclusion of benefit recipients or families.',
                    '<strong>Documentation Standards:</strong> Maintain detailed records of tenant selection decisions to demonstrate compliance with non-discriminatory practices in case of disputes or challenges.',
                    '<strong>Risk Mitigation:</strong> While tenant oversupply may reduce practical impact, ensure robust financial vetting processes that comply with anti-discrimination requirements while protecting investment interests.'
                ]
            }
        },
        'pets': {
            'title': 'Pets',
            'explainer': {
                'title': 'New Pet Regulations Under RRA',
                'content': [
                    'The RRA implies into all private sector APTs a right for the tenant to keep a pet at the property with the landlord\'s consent, which is not to be unreasonably withheld.',
                    'The tenant\'s request for consent must be in writing and include a description of the pet and the landlord will need to give or refuse consent within 28 days. That timeframe is extended where the landlord reasonably requires further information or a superior landlord\'s consent is required, or if the parties simply agree to a longer period.',
                    'There is no requirement for superior landlords not to unreasonably withhold consent. The Act also confirms that it will be reasonable for the landlord to refuse consent where the superior lease requires superior landlord\'s consent which has not been given, provided the landlord has taken reasonable steps to obtain it. In cases where the superior lease contains an absolute bar on keeping pets, the landlord does not need to take steps to get the superior landlord to consent.',
                    'Government guidance is expected as to other situations where it might be reasonable for the landlord to refuse consent, for example because of the size of property or the number of existing pets kept by the tenant, but this will depend on individual circumstances and would ultimately be up to the courts or the ombudsman.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Maintenance Cost Increase:</strong> Having pets in a rental property can significantly impact a landlord\'s costs of repairs. Pets, especially dogs and cats, may cause damage to flooring, carpets, and walls through scratching, chewing, or staining.',
                    '<strong>Additional Cleaning Expenses:</strong> Additionally, pet-related issues like odor build-up, hair accumulation, and pest infestations can lead to cleaning and pest control expenses. Over time, these damages often necessitate costly repairs or replacements to maintain the property\'s condition.',
                    '<strong>Budget Allocation:</strong> Consequently, landlords may need to allocate a higher budget for maintenance and repairs to address pet-related wear and tear, which can also influence rental fees or refundable deposits.',
                    '<strong>Response Timeline:</strong> Must respond to written pet requests within 28 days (or extended period if additional information needed or superior landlord consent required).',
                    '<strong>Reasonable Refusal Grounds:</strong> Can refuse consent for reasonable grounds such as property size limitations, existing pet numbers, superior lease restrictions, or specific property characteristics.',
                    '<strong>Superior Lease Considerations:</strong> Where superior leases require consent, must take reasonable steps to obtain it. Absolute pet bans in superior leases provide valid grounds for refusal without further action required.',
                    '<strong>Documentation Requirements:</strong> Ensure all pet consent decisions are properly documented with written reasons for any refusals to demonstrate reasonableness.',
                    '<strong>Insurance Implications:</strong> Review property insurance policies to understand coverage for pet-related damage and consider additional pet liability insurance requirements.',
                    '<strong>Deposit Strategy:</strong> Consider requesting additional refundable deposits specifically for pet-related damage, within legal limits for deposit amounts.',
                    '<strong>Property Protection:</strong> Implement reasonable conditions for pet keeping such as professional cleaning requirements, damage prevention measures, or regular property inspections.'
                ]
            }
        },
        'database': {
            'title': 'New Private Rented Sector Database',
            'explainer': {
                'title': 'Registration Requirements and Ombudsman Scheme',
                'content': [
                    'The RRA provides for the compulsory registration of landlords and properties on a new private rented sector (PRS) database. This is designed to increase transparency for tenants and help local housing authorities target enforcement action.',
                    'All private landlords who rent out properties on ATs will be legally required to join a government-approved ombudsman scheme. This will apply whether the landlord manages the property themselves or uses an agent. Once this part of the RRA is in force, a property must not be marketed or offered for rent unless there are "active entries" on the database in respect of both the landlord and the property and any advert must include the allocated unique identifiers for them.',
                    'Landlords must then maintain active entries on the database throughout the tenancy and will not be able to obtain a possession order – other than on grounds of serious criminal or anti-social behaviour – unless such entries exist.',
                    'The scheme is designed to provide a quick, fair, and impartial alternative to the court system for resolving disputes between landlords and tenants. It aims to bring private renting in line with other sectors, such as social housing, where redress schemes are already mandatory.',
                    'Prospective, current and former tenants will be able to raise complaints about a wide range of issues, including poor communication, repair issues that are not addressed within a reasonable timeframe, or unfair practices.',
                    'Tenants must first attempt to resolve the issue directly with the landlord. If a resolution is not reached within a specified period (which will be set out in regulations), they can then take their complaint to the ombudsman.',
                    'The ombudsman\'s decisions will be legally binding on the landlord. The scheme will have the power to order landlords to take remedial action, provide an apology, or pay compensation (up to a certain limit).',
                    'Local authorities will be responsible for enforcement. Landlords who fail to join the scheme can face civil penalties of up to £7,000 for an initial breach, rising to £40,000 or criminal prosecution for continued non-compliance. Landlords will also be unable to serve certain possession notices if they are not registered with the scheme and the accompanying Private Rented Sector (PRS) Database.',
                    'Changes to the information that must be provided to tenants: The RRA will impose a new duty on landlords to provide a written statement of terms and other information before an AT is entered into. The exact terms and information required to be covered will be set out in future regulations, but the statement can include the notice of the landlord\'s wish to be able to recover possession on any of the statutory grounds for which advance notice must be given.',
                    'Transitional provisions will apply in relation to existing tenancies granted before the RRA comes into force. These provisions will require swift action by landlords. For existing written tenancies, the duty to provide the \'standard\' new statement of terms and information will not apply. Instead, landlords must give their tenants information about the changes made by the RRA, within a month after the RRA comes into force.',
                    'Exactly what information will need to be provided is to be set to in regulations. It is possible that the Secretary of State will issue a standard form document to be used.',
                    'These are tight timescales and unprepared landlords with large portfolios might struggle to comply. This underlines the importance of the sector being given sufficient notice of implementation.',
                    'Agents can comply with these duties on behalf of landlords and the duties will also apply to the agents themselves where they are under a relevant contractual obligation to the landlord.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Service Provider Mindset:</strong> The RRA fundamentally changes the game for private landlords, they now need to think of themselves as service providers and their tenant as their customer. Many landlords will struggle to adapt to this new reality, however, the consequences for not being able to deal with customer (tenant) complaints and repairs in a timely manner will likely have significant financial consequences.',
                    '<strong>Property Assessment:</strong> Landlords would be prudent to undertake the following work: Review their properties to determine if their current properties are in a clean and serviceable condition.',
                    '<strong>Preventative Maintenance:</strong> Have a planned preventative maintenance program to deal with issues before they become issues for the tenant.',
                    '<strong>Contractor Network:</strong> Have a list of basic contractors who can carry out maintenance works at relatively short notice.',
                    '<strong>Property Manager Agreements:</strong> If they have a property manager agree a pre-agreed budget for works they can undertake without approval and an approval process for higher cost jobs.',
                    '<strong>Self-Management Process:</strong> If landlords self-manage they will need to have a documented repair process in place with the tenant.',
                    '<strong>Registration Requirements:</strong> Must register both landlord and property details on the PRS database before marketing. All advertisements must include unique database identifiers.',
                    '<strong>Ombudsman Compliance:</strong> Mandatory participation in government-approved ombudsman scheme. Decisions are legally binding and can result in compensation orders.',
                    '<strong>Penalty Exposure:</strong> Civil penalties up to £7,000 for initial breach, rising to £40,000 or criminal prosecution for continued non-compliance.',
                    '<strong>Possession Restrictions:</strong> Cannot obtain possession orders (except for serious criminal/ASB grounds) without active database entries.',
                    '<strong>Information Duties:</strong> Must provide comprehensive written statements before tenancy commencement and RRA change notifications within one month for existing tenancies.',
                    '<strong>Tight Compliance Timescales:</strong> Large portfolio landlords may struggle with rapid implementation requirements. Early preparation essential.',
                    '<strong>Agent Responsibilities:</strong> Letting agents can fulfill obligations on behalf of landlords but are also directly liable for compliance.',
                    '<strong>Customer Service Standards:</strong> Must establish formal complaint handling procedures and rapid response systems to avoid ombudsman referrals.'
                ]
            }
        },
        'penalties': {
            'title': 'Penalties for Non-Compliance',
            'explainer': {
                'title': 'Enforcement and Penalties Under RRA',
                'content': [
                    'The RRA imposes a raft of new duties on landlords and agents with various sanctions for breach, including increased civil fines and new criminal offences for persistent or serious breach. Local housing authorities will be under a duty to take enforcement action and have been given enhanced investigative powers to assist them in this.',
                    'Specific duties and penalties: Landlords and agents will be under specific duties not to: purport to grant a fixed term AT (or AST); purport to terminate an APT by serving notice to quit orally or in writing; rely on a statutory ground for possession where they do not reasonably believe the landlord can obtain an order for possession on that ground; rely on one of the "advance notice grounds" for possession – grounds 1B, 2ZA to 2DZ, 4, 5 to 5H, 6A or 18 – where a statement of the landlord\'s wish to be able to use that ground was not included in any written statement of terms required to be given to the tenant.',
                    'Criminal offences and penalties: New criminal offences created by the Act include: relying on a ground for possession knowing that the landlord would not be able to obtain an order for possession on that ground, or being reckless as to whether the landlord would be able to do so, if the tenant surrenders the tenancy within four months without an order for possession being made.',
                    'Additional criminal offences include: contravening the restrictions on letting or marketing where ground 1 or ground 1A has been relied on. Agents will have a defence in relation to marketing if they can show they took all reasonable steps to avoid contravening the restriction.',
                    'Further offences cover: persistent or repeated breach of the other duties referred to in \'Specific duties and penalties\' above; knowingly or recklessly providing false or misleading information to the PRS database operator, or persistent or repeated failure to comply with the requirements in relation to the PRS database mentioned above; and persistent or repeated failure to comply with regulations requiring membership of the ombudsman scheme.',
                    'Financial penalties for breach can be up to £7,000 for an initial and less serious breach but can rise to up to £40,000 for serious, persistent or repeated breaches where a penalty is imposed rather than criminal prosecution. Local authorities are likely to be more proactive in enforcing the Act as they retain the financial penalties that they collect.',
                    'Initial or minor non-compliance will incur a civil penalty of up to £7,000 and serious, persistent or repeat non-compliance a civil penalty of up to £40,000, with the alternative of a criminal prosecution.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Enhanced Enforcement:</strong> Local housing authorities will be under a duty to take enforcement action and have been given enhanced investigative powers, making detection and prosecution more likely.',
                    '<strong>Escalating Penalty Structure:</strong> Financial penalties start at up to £7,000 for initial/minor breaches but escalate rapidly to £40,000 for serious, persistent, or repeated violations, with criminal prosecution as an alternative.',
                    '<strong>Criminal Liability Risks:</strong> New criminal offences with serious consequences for knowing or reckless violations, particularly around possession grounds and database compliance.',
                    '<strong>Specific Prohibited Actions:</strong> Cannot grant fixed-term tenancies, serve oral/written notice to quit, or rely on possession grounds without reasonable belief of success.',
                    '<strong>Advance Notice Requirements:</strong> Must include advance notice statements in written terms for specific possession grounds (1B, 2ZA to 2DZ, 4, 5 to 5H, 6A, 18) or face penalties for later reliance.',
                    '<strong>Marketing Restrictions:</strong> Strict limitations on letting/marketing after using grounds 1 or 1A, with potential criminal liability for violations.',
                    '<strong>Database Compliance:</strong> Criminal offences for knowingly providing false information or persistent failure to comply with PRS database requirements.',
                    '<strong>Ombudsman Scheme Penalties:</strong> Persistent failure to join mandatory ombudsman scheme constitutes criminal offence.',
                    '<strong>Local Authority Incentivization:</strong> Local authorities retain collected penalties, creating financial incentives for proactive enforcement action.',
                    '<strong>Agent Liability:</strong> Letting agents face same penalties and criminal liability, though some defences available if reasonable steps taken.',
                    '<strong>Compliance Investment Required:</strong> Need robust legal compliance systems, documentation processes, and professional advice to avoid severe financial and criminal consequences.',
                    '<strong>Repeat Offender Targeting:</strong> Escalating penalty structure particularly punishes persistent non-compliance, making ongoing violations extremely costly.'
                ]
            }
        },
        'timing': {
            'title': 'Timing',
            'explainer': {
                'title': 'Implementation Timeline and Phased Approach',
                'content': [
                    'While the RRA has gained Royal Assent, it does not come into effect immediately. Although no specific implementation period has yet been provided, it is anticipated the majority of provisions taking effect from Spring 2026.',
                    'However, these timings are uncertain and the Government retains the power to vary the implementation period for different parts of the Act. It is likely that the Government will seek to abolish section 21 Notices at the earliest opportunity, which may be some time before full implementation of the RRA.',
                    'In its guide to the then Bill, the government said the private rented sector would be given "sufficient notice ahead of implementation" and it said it would "work closely with all parties to ensure a smooth transition". However, no firm timetable has yet been issued.',
                    'Given the fundamental and far-reaching reforms under the Act, even a year after Royal Assent might seem ambitious to achieve that. However, we suspect the government will want to implement at least the new tenancy regime sooner than that, possibly as early as spring 2026, and that this might be accompanied by implementation of the anti-discrimination provisions and prohibition on rental bidding wars too.',
                    'An early version of the PRS database could also emerge before summer 2026, with the ombudsman service as well as the extension of Awaab\'s law and the Decent Homes Standard to follow later. However, these suggested timelines are only our best guesses.',
                    'What we do know is that landlords and their advisers should expect swathes of new detailed regulations, guidance and court forms to absorb over the coming months before the new tenancy regime comes into force, and beyond.',
                    'Given the practical difficulties that will arise, there will be transitional rules that will apply in relation to parts of the new legislation. For example, any section 21 notice or section 8 notice served, and any possession proceedings begun under the existing grounds of the Housing Act 1988 before the Act comes into force, will remain valid but landlords will need to comply with strict deadlines.',
                    'However, there will be a \'big bang\' day from which the new regime will apply to convert existing tenancies into ATs.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Uncertain Timeline:</strong> No firm implementation dates provided, creating planning difficulties for landlords. Majority of provisions expected Spring 2026 but government retains power to vary timing for different parts.',
                    '<strong>Phased Implementation Priority:</strong> Section 21 abolition likely to be implemented earliest, possibly before full RRA implementation. New tenancy regime, anti-discrimination provisions, and bidding war prohibition may follow by Spring 2026.',
                    '<strong>Preparation Window:</strong> Limited time to prepare for fundamental changes. Need to start preparation immediately despite uncertain timelines to avoid being caught unprepared.',
                    '<strong>Regulatory Burden:</strong> Expect \'swathes of new detailed regulations, guidance and court forms\' to absorb in coming months, requiring significant time investment for compliance preparation.',
                    '<strong>Transitional Complexity:</strong> Existing section 21 and section 8 notices served before implementation remain valid but with strict deadline compliance requirements. Need to understand transitional rules thoroughly.',
                    '<strong>Big Bang Conversion:</strong> All existing tenancies will convert to ATs on a specific implementation date, requiring immediate compliance with new regime across entire portfolio.',
                    '<strong>Database Readiness:</strong> Early PRS database version may emerge before Summer 2026, requiring registration preparation and system setup.',
                    '<strong>Ombudsman Preparation:</strong> Ombudsman service implementation may follow later, but preparation for complaint handling procedures should begin immediately.',
                    '<strong>Awaab\'s Law Extension:</strong> Property condition standards will be extended later in implementation phase, requiring property assessment and improvement planning.',
                    '<strong>Professional Advice Requirements:</strong> Given complexity and uncertain timing, ongoing legal and property management advice essential throughout transition period.',
                    '<strong>Training Investment:</strong> Staff, agents, and contractors will need extensive training on new procedures, requiring significant time and resource allocation.',
                    '<strong>System Upgrades:</strong> Property management systems, documentation processes, and compliance procedures will need comprehensive overhaul before implementation.'
                ]
            }
        },
        'awaabs_law': {
            'title': "Awaab's Law and the Decent Homes Standard",
            'explainer': {
                'title': 'Housing Standards Requirements Under RRA',
                'content': [
                    'The RRA provides for both Awaab\'s law and the Decent Homes Standard to apply to private sector tenancies. At the moment Awaab\'s law only applies to social housing, however, regulations will be needed to implement these.',
                    'Awaab\'s law will require landlords to take action to fix reported health and safety hazards within set limits. It is being introduced in phases in the social sector, and the government has said it will be consulting on the approach to implementation for the private sector in due course.',
                    'Separately, the government has consulted on reforming the Decent Homes Standard ahead of it applying to private as well as social sector tenancies. The government has still to confirm the outcomes from its consultation but has proposed that the new standard be enforceable from either 2035 or 2037.',
                    'Awaab\'s Law and the Decent Homes Standard are two interconnected government initiatives, primarily for social housing, that aim to improve living conditions and hold landlords accountable for property maintenance. The Renters\' Rights Act (RRA) is the legislation that facilitates the extension of these standards to the private rented sector.',
                    'Awaab\'s Law: Awaab\'s Law, enacted in the social rented sector in 2025, introduces strict, legally binding timeframes for social landlords to address serious health and safety hazards, particularly damp and mould, in response to the tragic death of Awaab Ishak.',
                    'Key requirements for social landlords include: Emergency hazards (e.g., gas leaks, major electrical faults, broken external doors/windows, severe damp/mould affecting health) must be investigated and made safe within 24 hours; Significant damp and mould hazards must be investigated within 10 working days; A written summary of the investigation findings must be provided to the tenant within 3 working days of the investigation concluding.',
                    'Additional requirements: Relevant safety work must begin within 5 working days of the investigation concluding; If the home cannot be made safe within the specified timeframes, the landlord must provide suitable alternative accommodation at their expense; Landlords must address the root cause of the issue, not just provide surface-level fixes; Tenants can take legal action for breach of contract if landlords fail to comply.',
                    'The law will be extended to cover a wider range of Housing Health and Safety Rating System (HHSRS) hazards in phases in 2026 and 2027.',
                    'The Decent Homes Standard (DHS): The Decent Homes Standard sets a minimum quality benchmark for rented homes. To meet the standard, a property must be: Free from the most serious health and safety hazards (Category 1 hazards under the HHSRS); In a reasonable state of repair (key building components must not be old and require replacement/major repair); Provided with reasonably modern facilities and services (e.g., modern kitchen and bathroom); Provided with a reasonable degree of thermal comfort (effective insulation and heating).',
                    'Relationship via the Renters\' Rights Act (RRA): The Renters\' Rights Act (which received Royal Assent in October 2025) is the primary vehicle for aligning and extending these standards across the rental sectors.',
                    'Extension to Private Rented Sector (PRS): The RRA introduces powers to apply the Decent Homes Standard to the private rented sector for the first time. It also commits to extending Awaab\'s Law to private landlords through future regulations, ensuring consistent protections for all tenants.',
                    'Interoperability: Awaab\'s Law effectively plugs a gap in the existing Decent Homes Standard by mandating specific, rapid timeframes for landlords to address serious hazards, which the original DHS did not specify. The RRA aligns the two, so that compliance with Awaab\'s Law timeframes becomes a component of meeting the broader Decent Homes Standard.',
                    'Enforcement: The RRA strengthens enforcement powers for local authorities and the Housing Ombudsman, ensuring landlords can be held accountable for non-compliance with both the DHS and Awaab\'s Law provisions.',
                    'In essence, Awaab\'s Law provides urgent, time-bound requirements for dealing with specific hazards, while the Decent Homes Standard sets the overall baseline quality expectation for rental properties, with the RRA expanding the scope of both across the housing sectors.'
                ]
            },
            'impact': {
                'title': 'Impact for Landlords',
                'content': [
                    '<strong>Strict Response Timeframes:</strong> When extended to private sector, landlords will face legally binding deadlines: 24 hours for emergency hazards, 10 working days for damp/mould investigation, 5 working days to begin safety work.',
                    '<strong>Emergency Response Requirements:</strong> Must be prepared to investigate and make safe gas leaks, major electrical faults, broken external doors/windows, and severe damp/mould affecting health within 24 hours.',
                    '<strong>Documentation Obligations:</strong> Written investigation summaries must be provided to tenants within 3 working days of investigation completion, requiring formal reporting processes.',
                    '<strong>Root Cause Solutions:</strong> Must address underlying causes of issues, not just surface-level fixes, potentially requiring significant structural or system improvements.',
                    '<strong>Alternative Accommodation Costs:</strong> If properties cannot be made safe within timeframes, must provide suitable alternative accommodation at landlord\'s expense, creating substantial cost exposure.',
                    '<strong>Phased HHSRS Expansion:</strong> Law will extend to wider range of Housing Health and Safety Rating System hazards in 2026-2027, broadening compliance obligations.',
                    '<strong>Decent Homes Standard Compliance:</strong> Properties must be free from Category 1 HHSRS hazards, in reasonable repair, with modern facilities and adequate thermal comfort by 2035-2037.',
                    '<strong>Property Upgrade Requirements:</strong> May need significant investment in heating systems, insulation, kitchen and bathroom modernization to meet Decent Homes Standard.',
                    '<strong>Enhanced Enforcement Powers:</strong> Local authorities and Housing Ombudsman will have strengthened powers to hold landlords accountable for non-compliance.',
                    '<strong>Legal Action Exposure:</strong> Tenants can take breach of contract action for non-compliance with Awaab\'s Law timeframes, creating additional legal risks.',
                    '<strong>Preventative Maintenance Investment:</strong> Need robust property inspection and maintenance systems to identify and address hazards before they become reportable issues.',
                    '<strong>Emergency Response Systems:</strong> Must establish 24/7 emergency response capabilities for urgent hazards, requiring contractor networks and rapid response procedures.',
                    '<strong>Long-term Investment Planning:</strong> DHS compliance by 2035-2037 requires strategic property improvement planning and significant capital investment over next decade.',
                    '<strong>Regulatory Consultation Preparation:</strong> Government consultation on private sector implementation approach requires active engagement to influence final requirements.'
                ]
            }
        }
    }
    
    # Get the current section content
    current_section = section_content.get(section_id)
    if not current_section:
        # Handle invalid section_id
        return render(request, 'rra_guide/section_not_found.html')
    
    # Get all sections for navigation
    all_sections = list(section_content.keys())
    current_index = all_sections.index(section_id)
    
    # Calculate next and previous sections
    next_section = all_sections[current_index + 1] if current_index < len(all_sections) - 1 else None
    prev_section = all_sections[current_index - 1] if current_index > 0 else None
    
    context = {
        'section': current_section,
        'section_id': section_id,
        'current_index': current_index + 1,
        'total_sections': len(all_sections),
        'next_section': next_section,
        'prev_section': prev_section,
        'progress_percentage': ((current_index + 1) / len(all_sections)) * 100
    }
    
    return render(request, 'rra_guide/section_detail.html', context)

@login_required
def rra_faqs(request):
    """
    Display FAQs section for the RRA guide
    """
    
    faqs = [
        # 1. Tenancy & Evictions (security of tenure and eviction rules)
        {
            'category': 'Tenancy & Evictions',
            'question': 'Can I still use fixed-term tenancies?',
            'answer': 'No. Fixed-term Assured Shorthold Tenancies (ASTs) are being abolished. All tenancies will become assured periodic tenancies (rolling contracts). Tenants can leave with 2 months\' notice. Landlord\'s lose the ability to lock tenants into 6- or 12-month contracts. Landlords have a term certain income of 2 months only. <br><br><strong>Implication for landlords:</strong> Less certainty of income, higher risk of voids, and stronger focus needed on tenant retention.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'Can I evict a tenant under Section 21 (no-fault eviction)?',
            'answer': 'No. Section 21 will be abolished. Landlords can no longer evict tenants without cause. <br><br><strong>Implication for landlords:</strong> You must prove one of the statutory grounds (e.g. arrears, antisocial behaviour, sale, or moving in).'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'What options do I have to evict a tenant under the new rules?',
            'answer': 'You must rely on the statutory grounds for possession. <strong>Mandatory grounds</strong> (court must grant): serious arrears, repeated arrears, moving in, selling. <strong>Discretionary grounds</strong> (judge decides): antisocial behaviour, breach of contract, property damage. <br><br><strong>Notice periods:</strong> Sale or move-in requires 4 months\' notice, and only after first 12 months of tenancy. Most others: 2 months\' notice.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'What happens if I want to sell or move back into the property?',
            'answer': 'You can regain possession of your property on statutory grounds for sale or occupation by yourself/close family, by serving a section 8 notice. You cannot use these grounds in the first 12 months of the tenancy. You must give 4 months\' notice after the 12 months has expired. You Must prove intent (e.g. marketing contract, family affidavit). The property cannot be re-let for 12 months after eviction to deter misuse.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'What are the new rules for selling a property with vacant possession?',
            'answer': 'You can regain possession of a property in order to sell it, but the Renters\' Rights Act 2025 now places strict evidential tests on landlords before a sale-based eviction will be granted. <br><br><strong>Key conditions:</strong> You cannot use the sale ground within the first 12 months of the tenancy; You must give the tenant at least 4 months\' notice after that period has elapsed; You must show a genuine intention to sell on the open market; The property must have been actively marketed for at least 6 months at a fair market price, with no suitable offers received. <br><br><strong>Evidence typically required:</strong> Dated marketing agreement or Rightmove/Zoopla advert; Confirmation from the selling agent showing six months of continuous marketing; Written statement (affidavit) explaining why no sale was achieved; Copy of the 4-month Section 8 notice citing the sale ground. <br><br><strong>Restrictions after possession:</strong> You cannot re-let or remarket the property for rent for 12 months following the tenant\'s departure.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'If I evict a tenant to move in myself, how long must I stay?',
            'answer': 'If you use the new section 8 "landlord occupation" ground, you (or an immediate family member) must intend to live in the property as your only or principal home for at least 6 months. You will usually need to provide an affidavit or other evidence of genuine intent (e.g. sale of your own home, job relocation, family circumstances). If you move out before 6 months, or never actually move in, this may be treated as a sham eviction which results in harsh penalties. <br><br><strong>Implication:</strong> You can only use this with genuine intent to move in and stay a minimum of 6 months. If you exercise section 8 eviction rights, you cannot relet for 12 months, so budget for 12 months of mortgage and other costs.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'What happens if a landlord is caught carrying out a sham eviction?',
            'answer': 'A sham eviction is when a landlord uses a legal ground (e.g. moving in themselves, selling the property) but never follows through, or only does so briefly to regain possession. <br><br><strong>Consequences:</strong> Rent Repayment Order (RRO): Tenant can claim up to 24 months\' rent; Civil penalties: Up to £7,000 per breach (stackable); Ombudsman: May award compensation (no statutory cap); Criminal liability: Could amount to unlawful eviction under the Protection from Eviction Act 1977 (unlimited fines/prison). <br><br><strong>Implication:</strong> Using false grounds for possession is high-risk. A sham eviction can wipe out up-to 2 years rental income, damage your reputation, and block future evictions.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'How are sham evictions exposed?',
            'answer': 'Former tenant complaint: After being evicted, the tenant notices the property is quickly re-let (e.g. advertised on Rightmove/Zoopla). They can then file a complaint with the council, the PRS Ombudsman, or make an application to the Tribunal for a Rent Repayment Order (RRO). <br><br><strong>Council checks:</strong> Councils already monitor letting adverts as part of fee/HMO enforcement. If a property is re-marketed soon after a landlord evicted on "move-in" or "sale" grounds, it raises a red flag. <br><br><strong>Evidence sources tenants may use:</strong> Online listings showing the property re-let at higher rent; Witness statements from neighbours; Council tax or utility bills in someone else\'s name; Social media or word-of-mouth if the property was quickly sold/let.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'Can I sell with a tenant in situ?',
            'answer': 'Yes. The tenancy transfers to the new owner. Maybe attractive to some investors / institutions at a price reflective of risk. Less attractive to other independent landlords. Less attractive to owner-occupiers.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'How long does eviction now take, realistically?',
            'answer': '<strong>A) Sale / Move Back In grounds (1 & 1A):</strong> Notice: Minimum 4 months; Earliest use: Only after 12 months of tenancy; If undisputed: Tenant moves out → process can be done in 4 months; If disputed: Could stretch to 5–6 months; Absolute worst case: 10–12 months with tribunal backlogs. <br><br><strong>B) Breach grounds (arrears, anti-social behaviour, etc.):</strong> Notice usually 2-4 weeks; Tenant disputes → tribunal process begins; If tenant digs heels in, even a "serious breach" case could run to 10–13 months before vacant possession is achieved. <br><br><strong>Implication:</strong> Landlords must budget for long delays and lost rent when trying to evict tenants.'
        },
        {
            'category': 'Tenancy & Evictions',
            'question': 'Can I restrict what tenants I accept?',
            'answer': 'Yes, but only on neutral, consistently-applied criteria. You cannot discriminate against applicants with children or on benefits (no "No DSS/No children" policies, and no indirect workarounds like higher deposits or extra months\' rent for those cohorts). <br><br><strong>Do:</strong> Publish a neutral ad with the stated rent (rental-bidding is banned); Apply one affordability policy to everyone; document decisions. <br><br><strong>Don\'t:</strong> Don\'t use blanket phrases like "No DSS/No children."; Don\'t require higher deposits or extra upfront rent for benefits/children applicants if you don\'t do the same for others. <br><br><strong>Consequences for breach:</strong> England: civil penalty up to £7,000.'
        },

        # 2. Rent (rent setting and reviews)
        {
            'category': 'Rent Setting & Reviews',
            'question': 'How are rent rises handled?',
            'answer': 'Landlords can increase the rent once every 52 weeks using the Section 13 notice procedure (Form 4). If the rent was increased previously by agreement (not via Section 13), a notice can still be used without waiting another 52 weeks.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'How much notice does a landlord need to give to increase the rent?',
            'answer': 'For a standard periodic tenancy with rent paid monthly, a landlord must give at least one month\'s notice of a rent to end at the beginning of the new tenancy period to increase the rent using Section 13.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'Can tenants challenge rent increases?',
            'answer': 'Yes. Tenants can refer the notice to the First-tier Tribunal (Property Chamber) before the date it is due to take effect. The Tribunal can confirm, reduce, or increase the rent to the open market level. During the dispute, the tenant must keep paying the old rent until the Tribunal decides.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'What happens if the Tribunal decides in favour of the landlord?',
            'answer': 'If the Tribunal sets the rent at the landlord\'s proposed level (or higher), the increase takes effect from the Tribunal\'s determination date or the next rent period after that. ⚠️ <strong>Importantly:</strong> rent cannot be backdated to the original notice date. The Tribunal may delay the effective date for hardship reasons, but by no more than 2 months.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'Does this mean tenants can build up arrears during a dispute?',
            'answer': 'No. If the tenant loses, they simply start paying the new rent from the Tribunal\'s decision (or up to 2 months later if hardship is considered). There is no debt for the period while the dispute was pending.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'How does the Tribunal decide on a rent dispute?',
            'answer': 'The tribunal will set a rent for the property. To do this, they will assess what rent the property would reasonably achieve if let on the open market under a new tenancy on the same terms. It considers both sides\' evidence (adverts, comparable, tenancy details). Tenants don\'t need professional evidence; they can use online listings or local adverts. Landlords often commission a RICS valuation or provide comparables to strengthen their case. So long as the proposed rent increase is no more than the average for a similar property in the area, the tribunal is unlikely to decrease the rent. <br><br><strong>Costs:</strong> Each side pays their own costs. <br><br><strong>Implication:</strong> Tenants can challenge cheaply, but you may need to spend on evidence. Tribunal decisions are unpredictable.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'How long does the rent increase process take?',
            'answer': 'Serve notice: landlord gives at least 1 month\'s notice; Tenant can dispute any time before the effective date; Tribunal hearing & determination: expected delays of 6–12 months in early years due to case backlogs; Rent increase then starts from the Tribunal decision date (or next rent period). <br><br><strong>Implication for landlords:</strong> Cashflow is delayed if tenants dispute — you may wait months before the increase is felt. But you won\'t receive backdated arrears, so planning cashflow is essential.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'Can I advertise \'offers over\' or accept bids above guide price?',
            'answer': 'No. Rent bidding wars are banned. Must advertise at a fixed rent. Cannot accept offers above.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'Upfront Rent – What\'s Allowed vs. Banned?',
            'answer': 'Only for the first rent period (e.g. one month). You cannot require multiple months in advance either before or during the tenancy. <br><br><strong>Before or at the start of tenancy:</strong> ✅ Landlords can still ask for the first rent payment in advance; ✅ If both sides agree at the outset, tenants can offer to pay multiple months up front as part of the initial agreement; ❌ But landlords cannot make it a blanket condition. <br><br><strong>After the tenancy has started:</strong> ❌ Landlords cannot demand extra rent in advance once the tenancy is underway; ✅ A tenant may voluntarily offer to pay future rent early.'
        },
        {
            'category': 'Rent Setting & Reviews',
            'question': 'Is there any enforcement of unlawful upfront rent requests?',
            'answer': 'Yes! And it covers attempts as well as actual collection. If a landlord or agent asks for (requests) or stipulates (requires) more than one month\'s rent upfront, it is a breach — even if the tenant never pays it. <br><br><strong>Who enforces?</strong> Local authorities (Trading Standards or Housing Enforcement teams). <br><br><strong>Penalties:</strong> Civil penalties: Up to £7,000 per breach; Criminal offence for repeat breaches: unlimited fine, possible banning order; Tenants can apply Rent Repayment Order (up to 24 months\' rent) via the Tribunal. <br><br><strong>Implication:</strong> Even a "try on" — e.g. telling a tenant "we prefer 6 months upfront" — is enough to trigger council enforcement.'
        },

        # 3. Deposits & fees (deposit caps, deposit schemes & PI)
        {
            'category': 'Deposits & Fees',
            'question': 'What is the maximum deposit?',
            'answer': 'No change: deposit cap remains at 5 weeks\' rent (or 6 weeks for high-rent tenancies).'
        },
        {
            'category': 'Deposits & Fees',
            'question': 'Do I need to register the deposit in a deposit scheme?',
            'answer': 'Yes. All deposits must be placed in a government-approved scheme with prescribed information issued within 30 days. 1. Protect the tenant\'s deposit in a government-approved scheme within 30 days. 2. Provide the tenant with the scheme\'s Prescribed Information (PI) within the same 30 days.'
        },
        {
            'category': 'Deposits & Fees',
            'question': 'What happens if I miss the 30-day deadline?',
            'answer': 'Tenants can claim compensation of 1–3 times the deposit, and you cannot serve a valid notice until the breach is remedied. <br><br><strong>Tenant\'s rights:</strong> The tenant can apply to court for compensation of 1 to 3 times the deposit amount, in addition to the return of the deposit itself. The court has no discretion to deny the award if the deposit was not properly protected. <br><br><strong>Likelihood of penalty:</strong> The path to a penalty is effectively guaranteed if the tenant brings a claim. Courts almost always award at least 1× the deposit; repeat or serious failures usually see 2× or 3×. <br><br><strong>Implication:</strong> Failing the 30-day rule is one of the easiest ways for landlords to be sued — and defending it is nearly impossible.'
        },
        {
            'category': 'Deposits & Fees',
            'question': 'Can I charge a pet deposit?',
            'answer': 'Yes. The final Renters\' Rights Act 2025 allows landlords to take a separate pet damage deposit of up to three weeks\' rent, in addition to the standard tenancy deposit. <br><br><strong>Key rules:</strong> The pet deposit must be protected in an approved deposit scheme within 30 days, and Prescribed Information must be served to the tenant; It can only be used to cover pet-related damage or cleaning beyond fair wear and tear; It is not subject to the normal 5-week cap for tenancy deposits; As an alternative, landlords may ask tenants to obtain pet damage insurance instead.'
        },
        {
            'category': 'Deposits & Fees',
            'question': 'What decides whether the court awards 1×, 2×, or 3× the deposit as a fine?',
            'answer': 'The judge chooses the multiplier (1–3×) based on the circumstances. <br><br><strong>Key factors include:</strong> Was the deposit eventually protected? (Protected late but eventually compliant → usually 1×; Never protected at all → higher, typically 2× or 3×); Prescribed Information (PI) served? (PI served after 30 days → still a breach; courts lean to 1×; PI never served at all → often 2× or 3×); Landlord\'s conduct: (First-time, genuine mistake, quickly remedied → 1×; Repeat offender or deliberate avoidance → 2× or 3×; Bad faith → almost always 3×). <br><br><strong>Implication:</strong> Even a technical breach guarantees at least 1× penalty. Once the tenant brings a claim, liability is automatic.'
        },
        {
            'category': 'Deposits & Fees',
            'question': 'How long do tenants have to bring a deposit penalty claim?',
            'answer': 'Tenants have up to 6 years from the date of the breach to bring a claim in the county court. This applies even if the tenancy has already ended and the tenant has moved out. <br><br><strong>Practical effect:</strong> A former tenant can come back years later and sue for a 1–3× deposit penalty, even if you already returned the deposit in full. Claims firms often target ex-tenants with "no win, no fee" offers. <br><br><strong>Implication:</strong> Keep dated proof of deposit protection and Prescribed Information service for at least 6 years after tenancy end.'
        },
        {
            'category': 'Deposits & Fees',
            'question': 'If I buy a buy-to-let with a tenant in situ, am I liable for any deposit breaches by the previous landlord?',
            'answer': 'Yes, liability transfers. Under the Housing Act 2004, the "landlord" at the time the claim is made is responsible — even if the original breach happened under the previous owner. <br><br><strong>Due diligence is critical:</strong> Always confirm, in writing, that the deposit has been protected in an approved scheme and that PI has been served. On completion, ensure the deposit is properly transferred to your nominated scheme and that fresh Prescribed Information is served within 30 days. <br><br><strong>Implication:</strong> Buying with tenants in situ is high risk if compliance history is unclear. Strong warranties and indemnities in the purchase contract are essential.'
        },

        # 4. Tenant Fees & Holding Deposits
        {
            'category': 'Tenant Fees & Holding Deposits',
            'question': 'Can I charge the tenant fees?',
            'answer': 'No. All fees are banned except those already allowed (replacement keys, rent arrears interest, etc.).'
        },
        {
            'category': 'Tenant Fees & Holding Deposits',
            'question': 'What fees can I legally charge tenants?',
            'answer': 'There are only a narrow list of permitted payments allowed under the Tenant Fees Act 2019: Rent (including arrears or agreed increases); Tenancy deposit (max 5 weeks\' rent, or 6 weeks if rent > £50,000 a year); Holding deposit (max 1 week\'s rent, with strict rules); Utilities, council tax, TV licence, phone/broadband (if included in the tenancy); Default fees for: Late rent (interest at up to 3% above Bank of England base rate); Replacing lost keys/security devices (reasonable cost only); Early termination charges, but only for the landlord\'s actual, reasonable loss.'
        },
        {
            'category': 'Tenant Fees & Holding Deposits',
            'question': 'What fees are banned?',
            'answer': 'Any payment not on the permitted list is unlawful. Common banned fees include: Admin/setup fees; Referencing or credit-check fees; Inventory/check-in/check-out fees; Tenancy renewal fees; Cleaning charges demanded upfront; "Pet rent" as a disguised fee (insurance may be required but not inflated rent or one-off "pet charges").'
        },
        {
            'category': 'Tenant Fees & Holding Deposits',
            'question': 'What happens if a landlord charges a banned fee?',
            'answer': 'In short, tenant can demand the money back and face civil enforcement penalties. Local authority can issue a civil penalty up-to £7,000 for a first breach. A second breach within 5 years is a criminal offence: Unlimited fine for second breach; Risk of banning order (prohibiting you from letting property). Tenants can apply to the First-tier Tribunal to reclaim unlawful fees.'
        },
        {
            'category': 'Tenant Fees & Holding Deposits',
            'question': 'Can a landlord still ask for a guarantor?',
            'answer': 'Yes. Landlords can still require a guarantor as a condition of granting a tenancy, usually where the tenant\'s income or credit history doesn\'t meet affordability checks. But under the new rules: Landlords cannot use a guarantor requirement in a way that amounts to discrimination; Guarantor agreements must remain clear, written, and signed; Tenants are still protected from banned fees — you cannot charge the tenant or guarantor for the cost of setting up a guarantee. <br><br><strong>Implication:</strong> Guarantors remain a valid risk-management tool, but landlords must ensure guarantor policies are applied fairly and consistently.'
        },

        # 5. PRS Database & Redress schemes registration
        {
            'category': 'PRS Database & Redress Schemes',
            'question': 'Do I need to register as a landlord?',
            'answer': 'Yes. The new PRS Database is mandatory. You must register yourself and your properties. Details must be kept up to date. Fees will apply. Letting or advertising without registration is unlawful.'
        },
        {
            'category': 'PRS Database & Redress Schemes',
            'question': 'What happens if I don\'t register?',
            'answer': 'First offence will receive a fixed penalty, repeat offences can become criminal and result in unlimited fines, landlords are barred from serving eviction notices. <br><br><strong>Penalties:</strong> First offence: civil penalty of up-to £7,000; Repeat/serious offence: criminal offence with unlimited fine; Local authorities have clear powers to enforce. <br><br><strong>Impact on possession:</strong> While unregistered, you are barred from serving eviction notices. In some cases, this ban can last for up to 2 years. <br><br><strong>Tenant remedies:</strong> Tenants may apply for a rent repayment order covering the period the landlord was unregistered up to 24 months. <br><br><strong>Implication:</strong> Failing to register is a "strict liability" offence — there are no excuses.'
        },
        {
            'category': 'PRS Database & Redress Schemes',
            'question': 'Do I have to join a landlord redress scheme?',
            'answer': 'Yes. All residential landlords must be members of an approved/designated landlord redress scheme (the Ombudsman for private landlords).'
        },
        {
            'category': 'PRS Database & Redress Schemes',
            'question': 'What if my letting agent is already in the redress scheme?',
            'answer': 'The new mandatory Landlord Redress Scheme (the Ombudsman for private landlords) is separate from the existing letting agent redress schemes, landlords must join the scheme.'
        },
        {
            'category': 'PRS Database & Redress Schemes',
            'question': 'What are the penalties for not joining?',
            'answer': 'Civil financial penalty up to £7,000 for failing to join or for marketing when the landlord isn\'t a member. Repeat/continuing breaches escalate to an offence; the council may impose a financial penalty up to £40,000 as an alternative to prosecution.'
        },

        # 6. Decent Homes Standard (DHS)
        {
            'category': 'Decent Homes Standard',
            'question': 'What are Decent Homes Standards?',
            'answer': 'For the first time, the Renters\' Rights Bill applies the Decent Homes Standard (DHS) to the private rented sector. This sets a legal minimum quality threshold that all rented homes must meet. It covers: Safety & hazards – homes must be free of Category 1 hazards; State of repair – no major disrepair such as leaking roofs, rotten windows, unsafe stairs; Facilities – usable kitchen and bathroom of a reasonable modern standard; Energy efficiency – adequate insulation and heating.'
        },
        {
            'category': 'Decent Homes Standard',
            'question': 'What counts as a \'decent home\' in the private sector?',
            'answer': 'A property must: Be free of Category 1 hazards under the Housing Health and Safety Rating System (HHSRS); Provide adequate heating and insulation; Be in a reasonable state of repair (no leaking roof, rotten timbers, broken windows); Have a kitchen and bathroom in a usable, modern condition (draft guidance: kitchens ≤20 years old; bathrooms ≤30 years unless well maintained); Have safe electrics — usually evidenced by a valid EICR and compliance with 18th Edition Wiring Regulations.'
        },
        {
            'category': 'Decent Homes Standard',
            'question': 'What does "Awaab\'s Law" mean for private landlords?',
            'answer': 'Serious hazards (e.g. damp, mould and electrics) must be fixed within set legal timeframes once identified. This duty now applies to PRS as well as social landlords. <br><br><strong>Implication:</strong> landlords can no longer "slow walk" urgent repairs — Councils can act if landlords delay or ignore urgent repairs.'
        },
        {
            'category': 'Decent Homes Standard',
            'question': 'Will councils give me time to fix problems before fining me?',
            'answer': 'Yes, usually. The new Decent Homes Standard (DHS) has been built into the Housing Act 2004 enforcement framework. For most repair/condition issues, you should expect an improvement notice first with a deadline (e.g. 14–56 days depending on works). A civil penalty usually follows if you fail to comply with the notice or if the breach is severe/risky enough that the council decides to penalise immediately. <br><br><strong>Implication:</strong> Don\'t assume you\'ll always get "first a warning, then a fine". Councils must act on Type 1 failures and can jump straight to penalties if they see serious or repeated issues.'
        },
        {
            'category': 'Decent Homes Standard',
            'question': 'What are the DHS risks to the landlord?',
            'answer': 'Tactical complaints: Tenants can complain at no cost, even if baseless. <strong>Stacking penalties:</strong> A single DHS breach could mean: £7,000 civil fine (council); Up to 24 months\' rent repayment (Tribunal); Ombudsman compensation for poor handling (£300–£2,000). Documentation is critical: landlords need dated records of repairs, safety checks, and upgrades. Older stock: Victorian terraces, 1960s flats, and non-insulated homes could face £5k–£15k upgrade costs per unit.'
        },

        # 7. Tenant Rights, Pets & Documentation
        {
            'category': 'Tenant Rights, Pets & Documentation',
            'question': 'Do I have to accept pets?',
            'answer': 'You must consider requests. You can only refuse with good reason (e.g. property unsuitable, allergy in HMO). Optional pet deposit (3 weeks). If you refuse, the tenant has the option to make a complaint to the ombudsman.'
        },
        {
            'category': 'Tenant Rights, Pets & Documentation',
            'question': 'How would a pet complaint or enforcement work under the Renters\' Rights Bill?',
            'answer': 'Tenant can appeal to the ombudsman, who may issue a binding ruling. <br><br><strong>Tenant\'s right to request:</strong> Every tenant has the right to request permission to keep a pet. The landlord must give a written response within 42 days. Silence or "ignoring" the request is treated as a refusal. <br><br><strong>Landlord\'s grounds to refuse:</strong> You can only refuse on reasonable grounds, such as: Property unsuitable; Lease restrictions; Health/safety issues. Generic statements like "I don\'t accept pets" will not be valid. <br><br><strong>If the tenant disputes the refusal:</strong> They can escalate to the new Private Rented Sector Ombudsman. The Ombudsman will review whether your refusal was reasonable. If not, they can issue a binding order requiring you to allow the pet.'
        },
        {
            'category': 'Tenant Rights, Pets & Documentation',
            'question': 'What documents must I provide at the start of a tenancy and during the tenancy?',
            'answer': 'Written statement of tenancy terms; Prescribed deposit information; How to Rent guide; Compliance certificates (gas, EPC, EICR); Licence (if applicable). <br><br><strong>Ongoing documents:</strong> Annual Gas Safety Certificate; EICR renewals every 5 years; Updated "How to Rent" guide if a new tenancy begins; Smoke & carbon monoxide alarms; Evidence of repairs/maintenance.'
        },
        {
            'category': 'Tenant Rights, Pets & Documentation',
            'question': 'What happens if I fail to provide these required documents?',
            'answer': '<strong>Invalid possession notices:</strong> Failure to provide required documents may bar you from using certain possession grounds. <br><br><strong>Civil penalties:</strong> Councils can fine for missing or expired safety documents (e.g. up to £7,000 for breaches). <br><br><strong>Ombudsman complaints & awards:</strong> If a landlord fails to provide required information, tenants may complain to the Ombudsman for compensation (expected £500–£2,000). <br><br><strong>Rent repayment orders:</strong> Tenants can apply to the Tribunal to reclaim up to 24 months\' rent. <br><br><strong>Implication:</strong> Even a "technical breach" can give tenants significant leverage in disputes.'
        },

        # 8. Penalties & Enforcement
        {
            'category': 'Penalties & Enforcement',
            'question': 'What can landlords be fined for?',
            'answer': 'Not registering with the PRS database; Charging banned tenant fees; Failing to protect deposits or issue Prescribed Information on time; Failing to provide required tenancy documents (e.g. gas, EPC, EICR); Failing to meet the Decent Homes Standard; Unlawful eviction or tenant harassment; Refusing pets unreasonably; Breaching licence conditions (e.g. HMO or selective licensing).'
        },
        {
            'category': 'Penalties & Enforcement',
            'question': 'What penalties apply under the new regime?',
            'answer': 'Civil penalties: up to £7,000 per breach (stackable); Rent Repayment Orders: up to 24 months\' rent; Ombudsman compensation: no statutory cap (expected £300-2,000 range); Criminal offences: for unlawful eviction, harassment, or licensing failures. <br><br><strong>Can penalties stack?</strong> Yes. A single breach may trigger multiple sanctions (e.g. £7,000 fine + RRO + Ombudsman award).'
        },
        {
            'category': 'Penalties & Enforcement',
            'question': 'Can you show a worst-case exposure (single tenancy) example?',
            'answer': 'Assumptions: Monthly rent: £1,500; Rent Repayment Order (RRO): 24 month\'s rent = £36,000; Multiple civil penalties (e.g., PRS unregistered, DHS breach, illegal fee, missing safety doc): 4 × civil penalties £7,000 = £28,000; Ombudsman award (service failing/pets handling etc.): £2,000 (upper-end, typical); <strong>Total hit = £36,000 (RRO) + £28,000 (civil fines) + £2,000 (ombudsman) = £66,000.</strong> That\'s more than 44 months of rent at £1,500 pcm.'
        },
        {
            'category': 'Penalties & Enforcement',
            'question': 'Can I really be banned from letting?',
            'answer': 'Yes. Multiple serious breaches can lead to a banning order. Multiple or serious breaches can result in a banning order, prohibiting you from letting property or managing tenancies. Breach of a banning order is a criminal offence, punishable by an unlimited fine or up to 24 months\' prison. <br><br><strong>Implication:</strong> A banning order is effectively the end of your landlord business — you cannot legally rent out property. For portfolio landlords, a ban can trigger forced sales or transfer of management to others at a loss.'
        },
        {
            'category': 'Penalties & Enforcement',
            'question': 'Could I go to prison as a landlord?',
            'answer': 'Yes. Illegal eviction/harassment of tenants; Breaching a banning order once it is in place. In practice, most penalties are financial — but custodial sentences remain possible for extreme misconduct.'
        },
        {
            'category': 'Penalties & Enforcement',
            'question': 'Do tenants\' risk anything if their complaint fails?',
            'answer': 'No. Tenants face no penalty for raising complaints with councils, the Tribunal, or the Ombudsman — even if dismissed. This creates potential for gaming the system: tenants can delay rent increases or evictions at little personal risk. <br><br><strong>Implication:</strong> Landlords must assume that every complaint will be made, whether genuine or tactical. Even weak complaints can tie up time and resources, and delay rent increases or possession.'
        },

        # 9. Strategic Questions
        {
            'category': 'Strategic Questions',
            'question': 'What are the biggest risks for landlords?',
            'answer': 'Inability to rely on fixed terms; Stronger tenant challenge rights (rent, repairs, eviction); Multiple overlapping enforcement regimes; Financial exposure from stacked penalties and RROs.'
        },
        {
            'category': 'Strategic Questions',
            'question': 'What should landlords do now?',
            'answer': 'Focus on tenant retention and compliance; Prepare for PRS Database registration; Audit properties against the Decent Homes Standard; Proactively keep on top of maintenance; Budget for upgrades: EPC, insulation, boilers, kitchens, bathrooms; Budget for possible longer voids and compliance upgrades; Make sure you have good evidence for any rent increases; Improve tenant screening and communication to reduce disputes; Plan an exit route.'
        },
        {
            'category': 'Strategic Questions',
            'question': 'Should landlords sell?',
            'answer': 'Use Lexit app click here to evaluate your assets performance and liabilities.'
        },
        {
            'category': 'Strategic Questions',
            'question': 'What are my selling options under new regime?',
            'answer': '1. Sell with tenant in situ to another investors. 2. Sell to the tenant. 3. Evict tenant and sell VP to open market'
        },
        {
            'category': 'Strategic Questions',
            'question': 'Is buy-to-let still worth it under these rules?',
            'answer': 'Margins are tighter, compliance costs higher and risks of being fined are very high as tenants have few downsides for using the new enforcement rules in their favour. Independent landlords need to factor in: EPC and Decent Homes upgrade costs (£5k–£15k typical); Compliance/admin burden; Longer eviction timelines (10–13 months if contested); Likely a high percentage of tenants will challenge rent reviews; Still viable in high-demand areas or for professional-scale landlords who can absorb compliance costs.'
        },
        {
            'category': 'Strategic Questions',
            'question': 'Will small landlords leave the market?',
            'answer': 'Evidence already shows a steady exit of independent landlords, particularly those with 1–2 properties. Rising costs, mortgage rates, and compliance burdens make yields unattractive. Some landlords are selling up; others are switching to holiday lets or corporate lets (though these have their own risks). Many landlords are looking to invest into professionally managed funds to get exposure to residential real estate.'
        },
        {
            'category': 'Strategic Questions',
            'question': 'What can landlords do now to prepare?',
            'answer': 'Audit compliance: check deposits, prescribed Information, safety certificates, and documentation; Register early with the PRS database once available; Budget for upgrades: EPC, insulation, boilers, kitchens, bathrooms; Redraft tenancy agreements with legal advice to ensure compliance; Improve tenant screening and communication to reduce disputes; Consider structure: holding properties via a company can offer tax and liability benefits; Plan exit routes: weaker-performing properties may be better sold than upgraded. <br><br><strong>Implication:</strong> Survival in the new regime will require professionalism and planning. Landlords who treat letting as a casual sideline will struggle.'
        }
    ]
    
    context = {
        'faqs': faqs
    }
    
    return render(request, 'rra_guide/faqs.html', context)
