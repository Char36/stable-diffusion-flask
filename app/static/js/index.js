function imagine(e) {
    const prompt = $('#prompt');
    const height = $('#height');
    const width = $('#width');
    const samples = $('#samples');
    const rows = $('#rows');
    const iterations = $('#iterations');
    const generating = $('#generating');
    const output = $('#output')

    e.preventDefault();

    setIsLoading(true);

    const requestData = {
        prompt: prompt.val(),
        H: parseInt(height.val()),
        W: parseInt(width.val()),
        n_samples: parseInt(samples.val()),
        n_rows: parseInt(rows.val()),
        n_iter: parseInt(iterations.val())
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

            const imageContent = generateImageContent(data);
            // (imageContent, '_blank', `width=${width},height=${height}`);
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
