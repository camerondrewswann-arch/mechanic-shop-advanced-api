# Mechanic Shop Advanced API — Presentation Script

**Target length: approximately 3½–4½ minutes**

Hello, my name is Cameron Swann, and this is my Advanced Mechanic Shop API project.

This API helps a mechanic shop manage customers, mechanics, service tickets, and inventory parts in one system. Instead of tracking repair requests, mechanic assignments, and required parts separately, the API stores those resources in a relational database and connects them through clearly organized endpoints.

The project is built with Python and Flask using an application-factory structure. I separated the API into four blueprints: customers, mechanics, service tickets, and inventory. SQLAlchemy manages the database models and relationships, and Marshmallow validates request data and serializes the responses.

A customer can have several service tickets, so customers and tickets have a one-to-many relationship. Service tickets and mechanics have a many-to-many relationship because one ticket can use multiple mechanics and one mechanic can work on multiple tickets. Inventory parts and service tickets also have a many-to-many relationship because a repair can require several parts and the same kind of part can be used on many repairs.

For authentication, passwords are hashed before they are stored. A customer logs in through the customer login route and receives a JSON Web Token. Protected customer routes require that token in a Bearer authorization header. The `/customers/my-tickets` endpoint reads the customer ID from the token and only returns service tickets belonging to that customer.

I also completed the optional mechanic authentication challenge. Mechanics have a separate login route and receive a token containing the mechanic role. A mechanic token is required to update service tickets, assign or remove mechanics, add parts to tickets, and create, update, or delete inventory records.

The project uses Flask-Limiter to protect login and registration routes from too many repeated requests. It also has default rate limits for general API protection. Flask-Caching caches frequently requested list routes, including customers, mechanics, tickets, inventory, and mechanic rankings. The cache is cleared after database changes so later requests receive current information.

For the advanced queries, the customer list supports pagination with `page` and `per_page` query parameters. The `/mechanics/ranked` endpoint counts ticket relationships and orders mechanics from the most assigned tickets to the least. The service-ticket edit endpoint accepts `add_ids` and `remove_ids` and updates the ticket’s mechanic list in one request.

Now I’ll demonstrate the API in Postman.

First, I’ll call the health endpoint to show the application is running. Next, I’ll log in as the seeded customer. The Postman test saves the returned token, and I’ll use it to call `/customers/my-tickets` and create a new service ticket.

Then I’ll log in as the seeded mechanic. Using the mechanic token, I’ll create an inventory part, assign a mechanic to the ticket with the edit endpoint, and attach the inventory part to the ticket. When I retrieve the ticket, the response displays both the assigned mechanics and the attached parts.

Finally, I’ll demonstrate the paginated customers endpoint and the ranked mechanics endpoint. I’ll also show the terminal where the automated pytest suite passes. The tests cover token authentication, protected routes, rate limiting, pagination, inventory CRUD, mechanic ranking, and ticket relationships.

This completes my Advanced Mechanic Shop API. The full source code, exported Postman collection, test suite, and documentation are included in my GitHub repository. Thank you.

## Deployment correction note

During the deployment section, show that the repository keeps the `app/`, `tests/`, and `.github/workflows/` folders intact. Briefly open `/health` and `/docs` on the live Render URL, and show the successful GitHub Actions build, test, and deploy jobs.
