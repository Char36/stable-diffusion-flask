function imagine(e) {
    const prompt = $('#prompt');
    const height = $('#height');
    const width = $('#width');
    const samples = $('#samples');
    const rows = $('#rows');
    const iterations = $('#iterations');
    const output = $('#output')

    e.preventDefault();

    setIsLoading(true);

    const seedValue = $('#seed').val().trim();
    const seed = seedValue
        ? parseInt(seedValue)
        : null;

    const requestData = {
        prompt: prompt.val(),
        H: parseInt(height.val()),
        W: parseInt(width.val()),
        n_samples: parseInt(samples.val()),
        n_rows: parseInt(rows.val()),
        n_iter: parseInt(iterations.val()),
        seed: seed
    };

    $.ajax({
        url: '/imagine',
        type: 'POST',
        accept: 'application/json',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(requestData),
        dataType: 'json',
        success: (data) => {
            setIsLoading(false);

            if (data.error) {
                alert(data.error);
                return;
            }

            const imageContent = generateImageContent(data);
            output.html(imageContent);
        },
        error: (request, error) => {
            setIsLoading(false);
            alert('something went wrong, check backend console');
        }
    });

    return false;
}

function setIsLoading(isLoading) {
    $('#imagine_button').attr("disabled", isLoading);
    $('#generating').prop('hidden', !isLoading);
    $('#imagine-spinner').prop('hidden', !isLoading)

    $('#prompt').attr('disabled', isLoading);
    $('#height').attr('disabled', isLoading);
    $('#width').attr('disabled', isLoading);
    $('#samples').attr('disabled', isLoading);
    $('#rows').attr('disabled', isLoading);
    $('#iterations').attr('disabled', isLoading);
    $('#seed').attr('disabled', isLoading);

    if (isLoading) {
        $('#imagine-text').val("Loading...");
    } else {
        $('#imagine-text').val("Imagine");
    }
}

function generateImageContent(data) {
    return `
        <div>
            ${data.map(b64 => `<img src="data:image/png;base64,${b64}" alt="img" class="output-img"/>`)}
        </div>
        `
}
